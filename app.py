 

from os.path import join
from json import dumps
from flask import Flask, render_template, request, redirect, session, send_file
from flask_basicauth import BasicAuth

import colors
from model.dbi import Cursor
from objects.user import UserVue, UserModelName, UsersModel, RemoveUser, TeammateVue, TeammateModel, Teammates
from objects.team import TeamsModel, TeamOf, TeamVue, TeamLeave, TeamModelFromId, NoTeamError
from objects.objective import ObjectivesModel, ObjectiveVue, DeleteObjectiveVue, ObjectiveModelFromId
from objects.picture import PictureOfTeam, PictureVue, PicturesOfTeamModel, DeletePictureVue, AllPicturesModel
from objects.qrcode import QRCodeVue, QRCodesModel, QRCodeFromKey, QRDoesntExistError, FoundQRCodeVue

app = Flask(__name__)
app.secret_key = 'turbo prout prout'
app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'suce_mak'
basic_auth = BasicAuth(app)

@app.route('/')
def main_page():
	# if 'user' in session:
	# 	return redirect('/team/list?select=1')
	return render_template('main_page.html')

@app.route('/newuser')
def new_user():
	if 'name' not in request.args:
		return redirect('/')
	user = UserVue(request.args['name'])
	with Cursor() as cursor:
		if not user.send_db(cursor):
			return redirect('/')
		session['user'] = max(cursor.cursor.lastrowid, 1)
	return redirect('/team/list?select=1')

@app.route('/deleteuser')
def delete_user():
	""" supprime l'utilisateur specifie """
	user_id = request.args['user']
	with Cursor() as cursor:
		RemoveUser(user_id).send_db(cursor)
	return redirect('/admin')

@app.route('/team')
def my_team():
	if 'user' not in session:
		return redirect('/')
	user_id = session['user']
	with Cursor() as cursor:
		teammate = TeammateModel(cursor, user_id)
		team_id = int(request.args['team'] if 'team' in request.args else teammate.team_id)
		try:
			team = TeamModelFromId(cursor, team_id)
		except NoTeamError:
			return redirect('/team/list?select=0')
		teammates = Teammates(cursor, team.team_id)
		objs = sorted(ObjectivesModel(cursor).objectives, key=lambda obj: obj.points)
		pictures = PicturesOfTeamModel(cursor, team.team_id)
		edit = 'team' not in request.args or int(request.args['team']) == teammate.team_id
	return render_template('team_page.html', edit=edit, team=team, teammates=teammates.teammates, objectives=objs, pictures=pictures.pictures)

@app.route('/team/new')
def new_team():
	return render_template('new_team.html', colors=colors.Colors().colors)

@app.route('/team/new/go')
def new_team_go():
	if 'teamname' not in request.args:
		return redirect('/team/new')
	team_name = request.args['teamname']
	user_id = session['user']
	color = int(request.args['color'])
	with Cursor() as cursor:
		TeamVue(user_id, team_name, color).send_db(cursor)
	return redirect('/team')

@app.route('/team/list')
def user_page():
	if 'user' not in session:
		return redirect('/')
	user_id = session['user']
	with Cursor() as cursor:
		user = UserModelName(cursor, user_id)
		teammate = TeammateModel(cursor, user_id)
		teams = TeamsModel(cursor)
		select = int(request.args['select'])
		return render_template('team_list.html', select=select, user=user, teams=teams.teams, teammate=teammate)

@app.route('/team/join')
def team_join():
	if 'team' not in request.args:
		return redirect('/team/select')
	user_id = session['user']
	team_id = int(request.args['team'])
	with Cursor() as cursor:
		TeammateVue(user_id, team_id, 0).send_db(cursor)
	return redirect('/team')

@app.route('/team/leave')
def team_leave():
	user_id = session['user']
	with Cursor() as cursor:
		TeamLeave(user_id).send_db(cursor)
	return redirect('/team/list?select=1')

@app.route('/team/picture')
def picture():
	obj_id = request.args['obj_id']
	team_id = request.args['team']
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
				user_id = session['user']
				team_id = TeamOf(cursor, user_id).team_id
				obj_id = request.form['obj_id']
				pic = PictureVue(team_id, obj_id)
				pic.send_db(cursor)
			file.save(join('uploads', pic.filename))
	return redirect('/team')

@app.route('/team/picture/delete')
def delete_picture():
	user_id = session['user']
	obj_id = request.args['obj_id']
	with Cursor() as cursor:
		team_id = TeamOf(cursor, user_id).team_id
		DeletePictureVue(team_id, obj_id).send_db(cursor)
	return redirect('/team')

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
		obj = ObjectiveModelFromId(cursor, pic.objective_id)
		team = TeamModelFromId(cursor, pic.team_id)
		return render_template('random_picture.html', team=team, pic=pic, obj=obj)

@app.route('/qrcodes/<qr_key>')
def found_qrcode(qr_key):
	""" page quand quelqu'un trouve un qrcode """
	with Cursor() as cursor:
		user_id = session['user']
		team = TeamOf(cursor, user_id)
		try:
			qrcode = QRCodeFromKey(cursor, qr_key)
			firsttime = FoundQRCodeVue(team.team_id, qrcode.qr_id).send_db(cursor)
			return render_template('find_qr.html', team=team, exists=True, already=(not firsttime), qrcode=qrcode)
		except QRDoesntExistError:
			return render_template('find_qr.html', team=team, exists=False)

@app.route('/admin')
@basic_auth.required
def admin():
	""" sert la page d'administration """
	with Cursor() as cursor:
		objs = ObjectivesModel(cursor)
		teams = TeamsModel(cursor)
		users = UsersModel(cursor)
		qrcodes = QRCodesModel(cursor)
	return render_template('admin.html', objectives=objs.objectives,\
		teams=teams.teams, users=users.users, qrcodes=qrcodes.qrcodes)

@app.route('/admin/qrcodes/new')
@basic_auth.required
def add_qrcode():
	""" ajoute un nouveau qr code """
	points = request.args['points']
	descr = request.args['descr']
	with Cursor() as cursor:
		QRCodeVue(points, descr).send_db(cursor)
	return redirect('/admin')

@app.route('/admin/qrcodes/<qr_key>')
@basic_auth.required
def admin_qrcode_img(qr_key):
	""" retourne le png du qrcode demande """
	return send_file(join('qrcodes', qr_key + '.png'))

if __name__ == '__main__':
	app.run('0.0.0.0')
