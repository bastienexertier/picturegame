""" fichier controlleur de l'appli """

from os.path import join
from flask import Flask, render_template, request, redirect, session, send_file, Response
from flask_basicauth import BasicAuth

import colors
from model import db
from model.user import User, Team, load_medals
from model.objective import Objective, Picture, save_file
from model.qrcode import QRCode, FoundQR
from model.comment import Comment

app = Flask(__name__)
app.secret_key = 'turbo prout prout'
app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'suce_mak'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///model/test.db'
basic_auth = BasicAuth(app)

class NoUserError(Exception):
	""" une erreur si l'utilisateur n'est pas defini cote client """

@app.route('/')
def index():
	""" redirige vers home """
	return redirect('/home')

@app.route('/home')
def home():
	""" page principale """
	return render_template(
		'home_page.html',
		teams=load_medals(Team.query.all()),
		users=User.query.order_by('name').all(),
		user=User.query.get(session.get('user', None)),
		admin=is_admin(),
		msg=request.args.get('msg', None)
	)

@app.route('/user', methods=['POST'])
def new_user():
	""" reception des donnees pour la creation d'un user """
	if 'name' in request.form and request.form['name']:
		user = User(name=request.form['name'].strip().capitalize())
		db.session.add(user)
		db.session.commit()
		session['user'] = user.id
	return redirect('/home')

# ================================= JOIN TEAM =================================

@app.route('/home/team/join')
def team_join():
	team = Team.query.get(request.args['team'])
	if 'team' not in request.args or team is None:
		return redirect('/home/team')

	user = User.query.get(getter_user(session))
	if not user.team:
		team.users.append(user)
		db.session.commit()
	return redirect(f'/team/{user.team.id}')

@app.route('/home/team/new')
def new_team():
	""" sert la page de creation d'equipe """
	return render_template('new_team.html', colors=colors.Colors())

@app.route('/home/team/new/go')
def new_team_go():
	""" ajoute la team dans le model """
	if 'teamname' not in request.args or 'color' not in request.args:
		return redirect('/home/team/new')

	if not (user := User.query.get(getter_user(session))).team:
		team = Team(
			name=request.args['teamname'].capitalize(),
			owner=user,
			color=int(request.args['color'])
		)
		team.users.append(user)
		db.session.add(team)
		db.session.commit()
	return redirect(f'/team/{user.team.id}')

# =================================== TEAM ====================================

@app.route('/team/<team_id>')
def my_team(team_id):
	""" si l'id de la team est donnee, on montre cette team, avec un acces en edition si c'est
	la team de user. Sinon, affiche la team de user avec edtiion """
	if not (team := Team.query.get(team_id)):
		return redirect('/home')

	user = User.query.get(session.get('user', None))
	is_my_team = user and user.team == team

	return render_template(
		'team_page.html',
		edit=is_my_team,
		is_admin=is_admin(),
		team=team,
		msg=request.args.get('msg', None),
		objectives=Objective.query.all(),
		qrs=QRCode.query.all(),
		user=user,
		pictures={pic.objective.id: pic for pic in team.pictures}
	)

@app.route('/team/leave')
def team_leave():
	""" un utilisateur qui quitte son equipe """
	user = User.query.get(getter_user(session))
	team = user.team
	if team.owner == user and len(team.users) > 1:
		return redirect(f'/team/{team.id}?msg=is-owner')

	team.users.remove(user)
	if not team.users:
		db.session.delete(team)
	db.session.commit()

	return redirect('/home')

@app.route('/team/picture', methods=['POST'])
def add_picture():
	if 'file' in request.files:
		file = request.files['file']
		if file.filename:
			team = User.query.get(getter_user(session)).team
			db.session.add(Picture(
				team=team,
				objective_id=int(request.form['id']),
				filename=save_file(file),
				status=0
			))
			db.session.commit()
	return redirect(f'/team/{team.id}')

@app.route('/team/picture/delete')
def delete_picture():
	""" supprime l'image si user est l'owner de son equipe """
	user = User.query.get(getter_user(session))
	pic = Picture.query.get(request.args['pic'])

	if pic.team.owner == user:
		db.session.delete(pic)
		db.session.commit()
	return redirect(f'/team/{user.team.id}')

@app.route('/team/owner')
def change_owner():
	""" change l'owner de lequipe """
	user = User.query.get(getter_user(session))
	new_owner = User.query.get(request.args['user'])
	if user.team and user.team.owner == user:
		user.team.owner = new_owner
		db.session.commit()
	return redirect(f'/team/{user.team.id}')

# ================================ OBJECTIVES =================================

@app.route('/picture/<pic_id>')
def send_picture(pic_id):
	""" sert l'image demandee """
	return send_file(join('uploads', pic_id))

@app.route('/picture')
def random_picture():
	""" sert la page d'imag aleatoire """
	from random import choice
	if (pic := choice(Picture.query.all())):
		return render_template('random_picture.html', pic=pic)
	return render_template('random_picture.html', pic=False)

@app.route('/qrcodes/<qr_key>')
def found_qrcode(qr_key):
	""" page quand quelqu'un trouve un qrcode """
	team = User.query.get(getter_user(session)).team
	found = FoundQR.query.get((team['id'], qr_key))
	qrcode = QRCode.query.get(qr_key)

	if not qrcode:
		return render_template('find_qr.html', team=team, exists=False)
	if not found:
		db.session.add(FoundQR(team_id=team['id'], qr_id=qr_key))
		db.session.commit()
	return render_template('find_qr.html', team=team, exists=True, already=found, qrcode=qrcode)

# ================================== COMMENT ==================================

@app.route('/comment', methods=['POST'])
def post_comment():
	""" post un commentaire """
	if (user_id := session.get('user', False)):
		pic = Picture.query.get(request.json['pic'])
		comment = Comment(text=request.json['text'], user_id=user_id)
		pic.comments.append(comment)
		db.session.commit()
		return Response(status=201)
	return Response(status=403)

# =================================== ADMIN ===================================

@app.route('/admin')
@basic_auth.required
def admin():
	""" sert la page d'administration """
	session['admin'] = 1
	teams = Team.query.all()
	invalid_pictures = {
		team: pics for team in teams
		if (pics := list(filter(lambda pic: pic.status == 0, team.pictures)))
	}
	return render_template(
		'admin.html',
		teams=teams,
		users=User.query.all(),
		pictures=invalid_pictures,
		objectives=Objective.query.all(),
		qrcodes=QRCode.query.all()
	)

@app.route('/admin/user/delete')
@basic_auth.required
def delete_user():
	""" supprime l'utilisateur specifie """
	user = User.query.get(request.args['user'])
	if (team := user.team):
		team.users.remove(user)
		if len(team.users) == 0:
			db.session.delete(team)
		elif team.owner == user:
			team.owner = User.query.filter_by(team_id=team.id).first()
	db.session.delete(user)
	db.session.commit()
	return redirect('/admin')

@app.route('/admin/objectives/new')
def new_obj():
	""" creer un nouvel objectif """
	db.session.add(Objective(
		points=request.args['points'],
		description=request.args['descr'])
	)
	db.session.commit()
	return redirect('/admin')

@app.route('/admin/objectives/delete')
def delete_obj():
	""" supprime un objectif """
	db.session.delete(Objective.query.get(request.args['obj']))
	db.session.commit()
	return redirect('/admin')

@app.route('/admin/picture/delete')
@basic_auth.required
def admin_delete_picture():
	""" suppression d'une photo en tant qu'admin """
	db.session.delete(Picture.query.get(request.args['pic']))
	db.session.commit()
	return redirect('/admin')

@app.route('/admin/picture/accept')
@basic_auth.required
def admin_accept_picture():
	""" changement du status d'une photo """
	Picture.query.get(request.args['pic']).status = 1
	db.session.commit()
	return redirect('/admin')

@app.route('/admin/qrcodes/new')
@basic_auth.required
def add_qrcode():
	""" ajoute un nouveau qr code """
	qrcode = QRCode(points=request.args['points'], description=request.args['descr'])
	db.session.add(qrcode)
	db.session.commit()
	return redirect('/admin')

@app.route('/admin/qrcodes/delete')
@basic_auth.required
def delete_qrcode():
	""" supprime le qrcode """
	db.session.delete(QRCode.query.get(request.args['qr']))
	db.session.commit()
	return redirect('/admin')

@app.route('/admin/qrcodes/<qr_key>')
@basic_auth.required
def admin_qrcode_img(qr_key):
	""" retourne le png du qrcode demande """
	return send_file(join('qrcodes', qr_key + '.png'))

# ============================ ERROR HANDLERS =================================

@app.errorhandler(NoUserError)
def handle_no_user_error(_):
	""" redirige le client vers la creation d'user si user nest pas defini """
	return redirect('/home')

# =================================== UTILS ===================================

def getter_user(session):
	""" retourne l'user_id si dans session, sinon exception """
	if 'user' not in session:
		raise NoUserError()
	return session['user']

def is_admin():
	return session.get('admin', 0) == 1

@app.route('/test')
def test_qr():
	return render_template('test_qr.html')

import init
init.main(app, db)
if __name__ == '__main__':
	app.run('0.0.0.0')
