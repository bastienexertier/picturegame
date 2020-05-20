""" fichier controlleur de l'appli """

from os.path import join
from flask import Flask, render_template, request, redirect, session, send_file
from flask_basicauth import BasicAuth

import colors
import getters
from model.dbi import Cursor

from objects.user import UserVue, UserModelName, RemoveUser
from objects.users import AllUsers, UsersFromTeam

from objects.teammate import TeammateVue

from objects.team import TeamsModel, TeamOf, TeamVue, TeamLeave, TeamModelFromId, NoTeamError, ChangeOwner

from objects.objective import ObjectivesModel, ObjectiveVue, DeleteObjectiveVue, ObjectiveModelFromId

from objects.picture import PictureOfTeam, PictureVue, DeletePictureVue, AcceptPictureVue
from objects.pictures import PicturesOfTeamModel, AllPicturesModel, PicturesWithStatus

from objects.qrcode import QRCodeVue, QRCodeFromKey, QRDoesntExistError, FoundQRCodeVue, RemoveQRCode
from objects.qrcodes import AllQRCodesModel, QRCodesOfTeam

app = Flask(__name__)
app.secret_key = 'turbo prout prout'
app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'suce_mak'
basic_auth = BasicAuth(app)

@app.route('/')
def main_page():
	if 'user' in session:
		return redirect('/home')
	return render_template('new_user.html')

@app.route('/newuser')
def new_user():
	if 'name' not in request.args:
		return redirect('/')
	user = UserVue(request.args['name'])
	with Cursor() as cursor:
		if not user.send_db(cursor):
			return redirect('/')
		session['user'] = max(cursor.cursor.lastrowid, 1)
	return redirect('/home')

@app.route('/home')
def home():
	""" """
	user_id = getters.user(session)
	with Cursor() as cursor:
		user = UserModelName(cursor, user_id)
		teams = TeamsModel(cursor)
		users = AllUsers(cursor)
		try:
			my_team = TeamOf(cursor, user_id)
		except NoTeamError:
			my_team = None
	return render_template('home_page.html', teams=teams, my_team=my_team, users=users, me=user)

# ================================= JOIN TEAM =================================

@app.route('/home/team/list')
def user_page():
	user_id = getters.user(session)
	with Cursor() as cursor:
		user = UserModelName(cursor, user_id)
		teams = TeamsModel(cursor)
		return render_template('team_list.html', user=user, teams=teams.teams)

@app.route('/home/team/join')
def team_join():
	# si l'user est supprime et qu'il essaye de rejoindre une team,
	# redirection vers team/list au lieu de user create
	if 'team' not in request.args:
		return redirect('/home/team/list')
	user_id = getters.user(session)
	team_id = int(request.args['team'])
	with Cursor() as cursor:
		TeammateVue(user_id, team_id, 0).send_db(cursor)
	return redirect('/team')

@app.route('/home/team/new')
def new_team():
	""" sert la page de creation d'equipe """
	return render_template('new_team.html', colors=colors.Colors())

@app.route('/home/team/new/go')
def new_team_go():
	""" ajoute la team dans le model """
	if 'teamname' not in request.args:
		return redirect('/home/team/new')
	team_name = request.args['teamname'].capitalize()
	user_id = getters.user(session)
	color = int(request.args['color'])
	with Cursor() as cursor:
		TeamVue(user_id, team_name, color).send_db(cursor)
	return redirect('/team')

# =================================== TEAM ====================================

@app.route('/team')
def my_team():
	""" si l'id de la team est donnee, on montre cette team, avec un acces en edition si c'est
	la team de user. Sinon, affiche la team de user avec edtiion """
	user_id = session.get('user', None)
	with Cursor() as cursor:

		team_id = -1
		try:
			team_id, is_my_team = get_team_id(cursor, user_id, request.args)
			team = TeamModelFromId(cursor, team_id)
		except NoTeamError:
			# permet de choisir une team si user n'en a pas
			return redirect('/home/team/list' if team_id == -1 else '/home')

		msg = request.args.get('msg', None)
		teammates = UsersFromTeam(cursor, team_id)
		objs = ObjectivesModel(cursor).to_sorted_list()
		pictures = PicturesOfTeamModel(cursor, team.team_id)
		all_qrs = AllQRCodesModel(cursor)
		team_qrs = QRCodesOfTeam(cursor, team_id)

	return render_template('team_page.html', edit=is_my_team, team=team,\
		teammates=teammates.users, objectives=objs, pictures=pictures.pictures, \
		qrs=all_qrs, team_qrs=team_qrs, user_id=user_id, msg=msg)

def get_team_id(cursor, user_id, args):
	""" essaye de trouver l'id de la team """
	try:
		team_of_user = TeamOf(cursor, user_id)
		team_id_of_user = team_of_user.team_id
	except NoTeamError:
		team_id_of_user = -1
	if 'team' in args:
		return int(args['team']), team_id_of_user == int(args['team'])
	return TeamOf(cursor, user_id).team_id, True

@app.route('/team/leave')
def team_leave():
	""" un utilisateur qui quitte son equipe """
	user_id = getters.user(session)
	with Cursor() as cursor:
		success = TeamLeave(user_id).send_db(cursor)
	msg = 'is owner'
	return redirect('/home') if success else redirect('/team?msg={}'.format(msg))

@app.route('/team/picture')
def picture():
	obj_id = int(request.args['obj_id'])
	team_id = int(request.args['team'])
	with Cursor() as cursor:
		pic = PictureOfTeam(cursor, team_id, obj_id)
		if pic.is_uploaded(cursor):
			return send_file(join('uploads', pic.filename))

@app.route('/team/picture/add', methods=['POST'])
def add_picture():
	if 'file' in request.files:
		file = request.files['file']
		if file.filename:
			with Cursor() as cursor:
				user_id = getters.user(session)
				team_id = TeamOf(cursor, user_id).team_id
				obj_id = request.form['obj_id']
				pic = PictureVue(team_id, obj_id)
				pic.send_db(cursor)
			file.save(join('uploads', pic.filename))
	return redirect('/team')

@app.route('/team/picture/delete')
def delete_picture():
	""" supprime l'image si user est l'owner de son equipe """
	user_id = getters.user(session)
	obj_id = int(request.args['obj_id'])
	with Cursor() as cursor:
		team = TeamOf(cursor, user_id)
		if team.is_owned_by(user_id):
			DeletePictureVue(team.team_id, obj_id).send_db(cursor)
	return redirect('/team')

@app.route('/team/owner')
def change_owner():
	""" change l'owner de lequipe """
	user_id = getters.user(session)
	new_owner = int(request.args['user'])
	with Cursor() as cursor:
		team = TeamOf(cursor, user_id)
		if team.is_owned_by(user_id):
			ChangeOwner(team.team_id, new_owner).send_db(cursor)
	return redirect('/team')

# ================================ OBJECTIVES =================================

@app.route('/objectives/new')
def new_obj():
	points = request.args['points']
	descr = request.args['descr']
	with Cursor() as cursor:
		ObjectiveVue(points, descr).send_db(cursor)
	return redirect('/admin')

@app.route('/objectives/delete')
def delete_obj():
	obj_id = request.args['obj_id']
	with Cursor() as cursor:
		DeleteObjectiveVue(obj_id).send_db(cursor)
	return redirect('/admin')

@app.route('/picture/<pic_id>')
def send_picture(pic_id):
	return send_file(join('uploads', pic_id))

@app.route('/picture')
def random_picture():
	with Cursor() as cursor:
		pics = AllPicturesModel(cursor)
		pic = pics.random_picture()
		if pic:
			obj = ObjectiveModelFromId(cursor, pic.objective_id)
			team = TeamModelFromId(cursor, pic.team_id)
			return render_template('random_picture.html', team=team, pic=pic, obj=obj)
		return render_template('random_picture.html', pic=False)

@app.route('/qrcodes/<qr_key>')
def found_qrcode(qr_key):
	""" page quand quelqu'un trouve un qrcode """
	with Cursor() as cursor:
		user_id = getters.user(session)
		team = TeamOf(cursor, user_id)
		try:
			qrcode = QRCodeFromKey(cursor, qr_key)
			already = not FoundQRCodeVue(team.team_id, qrcode.qr_id).send_db(cursor)
			return render_template('find_qr.html', team=team, exists=True, already=already, qrcode=qrcode)
		except QRDoesntExistError:
			return render_template('find_qr.html', team=team, exists=False)

# =================================== ADMIN ===================================

@app.route('/admin')
@basic_auth.required
def admin():
	""" sert la page d'administration """
	with Cursor() as cursor:
		objs = ObjectivesModel(cursor)
		teams = TeamsModel(cursor)
		users = AllUsers(cursor)
		invalid_pictures = PicturesWithStatus(cursor, 0)
		qrcodes = AllQRCodesModel(cursor)
	return render_template('admin.html', objectives=objs, teams=teams,\
		users=users, pictures=invalid_pictures.pictures, qrcodes=qrcodes.qrcodes)

@app.route('/admin/user/delete')
@basic_auth.required
def delete_user():
	""" supprime l'utilisateur specifie """
	user_id = request.args['user']
	with Cursor() as cursor:
		TeamLeave(user_id).send_db(cursor)
		RemoveUser(user_id).send_db(cursor)
	return redirect('/admin')

@app.route('/admin/picture/delete')
@basic_auth.required
def admin_delete_picture():
	""" suppression d'une photo en tant qu'admin """
	team_id = request.args['team']
	obj_id = request.args['obj']
	with Cursor() as cursor:
		DeletePictureVue(team_id, obj_id).send_db(cursor)
	return redirect('/admin')

@app.route('/admin/picture/accept')
@basic_auth.required
def admin_accept_picture():
	""" changement du status d'une photo """
	team_id = request.args['team']
	obj_id = request.args['obj']
	with Cursor() as cursor:
		AcceptPictureVue(team_id, obj_id).send_db(cursor)
	return redirect('/admin')

@app.route('/admin/qrcodes/new')
@basic_auth.required
def add_qrcode():
	""" ajoute un nouveau qr code """
	points = request.args['points']
	descr = request.args['descr']
	with Cursor() as cursor:
		QRCodeVue(points, descr).send_db(cursor)
	return redirect('/admin')

@app.route('/admin/qrcodes/delete')
@basic_auth.required
def delete_qrcode():
	""" supprime le qrcode """
	qr_id = request.args['qr']
	with Cursor() as cursor:
		RemoveQRCode(qr_id).send_db(cursor)
	return redirect('/admin')

@app.route('/admin/qrcodes/<qr_key>')
@basic_auth.required
def admin_qrcode_img(qr_key):
	""" retourne le png du qrcode demande """
	return send_file(join('qrcodes', qr_key + '.png'))

# ============================ ERROR HANDLERS =================================

@app.errorhandler(getters.NoUserError)
def handle_no_user_error(_):
	""" redirige le client vers la creation d'user si user nest pas defini """
	return redirect('/')

@app.errorhandler(NoTeamError)
def handle_no_team_error(_):
	""" redirige le client vers la selection d'equipe si une erreur survient """
	return redirect('/team/list')

if __name__ == '__main__':
	app.run('0.0.0.0')
