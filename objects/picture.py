
from random import choice
from string import ascii_lowercase
from os.path import isfile, join

from objects.jsonable import Vue, Model
import model.requests as req

class Picture:
	def __init__(self, team_id, objective_id):
		self.team_id = team_id
		self.objective_id = objective_id

	def is_uploaded(self, cursor):
		return bool(cursor.get(req.get_picture(), (self.team_id, self.objective_id)))

class PictureVue(Picture, Vue):
	def __init__(self, team_id, objective_id):
		super().__init__(team_id, objective_id)
		self.filename = self.__create_filename()

	def __create_filename(self):
		while True:
			filename = ''.join(choice(ascii_lowercase) for i in range(10)) + '.jpg'
			if not isfile(join('uploads', filename)):
				return filename

	def _check(self, cursor):
		return not self.is_uploaded(cursor)

	def _send_db(self, cursor):
		cursor.add(req.add_picture(), (self.team_id, self.objective_id, self.filename, 0))

class PictureModel(Picture, Model):
	def __init__(self, team_id, objective_id, filename, status):
		super().__init__(team_id, objective_id)
		self.filename = filename
		self.status = status

class PictureOfTeam(PictureModel):
	def __init__(self, cursor, team_id, objective_id):
		self.cursor = cursor
		filename, status = self.__get_info(team_id, objective_id)
		super().__init__(team_id, objective_id, filename, status)

	def __get_info(self, team_id, objective_id):
		pic = self.cursor.get_one(req.picture_of_team(), (team_id, objective_id))
		return pic['filename'], pic['status']

class PicturesModel(Model):
	def __init__(self, cursor, pictures):
		self.cursor = cursor
		self.pictures = pictures

	def _load_pictures(self, cursor, req, args):
		res = {}
		req_res = cursor.get(req, args)
		for pic in req_res:
			team_id = pic['team_id']
			if team_id not in res:
				res[team_id] = {}
			obj_id = pic['objective_id']
			filename = pic['filename']
			status = pic['status']
			res[team_id][obj_id] = PictureModel(team_id, obj_id, filename, status)
		return res

class PicturesOfTeamModel(PicturesModel, Model):
	def __init__(self, cursor, team_id):
		self.team_id = team_id
		load_req = req.get_team_pictures()
		args = (self.team_id,)
		super().__init__(cursor, self._load_pictures(cursor, load_req, args).pop(team_id, {}))

class AllPicturesModel(PicturesModel, Model):
	def __init__(self, cursor):
		load_req = req.get_all_pictures()
		super().__init__(cursor, self._load_pictures(cursor, load_req, ()))

	def random_picture(self):
		pic_list = []
		for team_pics in self.pictures.values():
			for pic in team_pics.values():
				pic_list.append(pic)
		return choice(pic_list)

class DeletePictureVue(Picture, Vue):
	def _check(self, cursor):
		return self.is_uploaded(cursor)

	def _send_db(self, cursor):
		cursor.add(req.delete_picture(), (self.team_id, self.objective_id))
