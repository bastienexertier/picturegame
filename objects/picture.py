""" module gerant les images """

# pylint: disable=too-few-public-methods

from random import choice
from string import ascii_lowercase
from os.path import isfile, join

from path import PATH
from objects.jsonable import Vue, Model
import model.requests as req

class Picture:
	""" un squelette d'image """
	def __init__(self, team_id, objective_id):
		self.team_id = team_id
		self.objective_id = objective_id

	def is_uploaded(self, cursor):
		""" verifie que l'image est bien dans la db """
		return bool(cursor.get(req.get_picture(), (self.team_id, self.objective_id)))

class PictureVue(Picture, Vue):
	""" une image ajoutee par un user """
	def __init__(self, team_id, objective_id, file):
		super().__init__(team_id, objective_id)
		self.filename = PictureVue.__create_filename()
		self.file = file

	@staticmethod
	def __create_filename():
		""" trouve un nom de fichier a donne a l'image, qui ne soit pas pris """
		while True:
			filename = ''.join(choice(ascii_lowercase) for i in range(10)) + '.jpg'
			if not isfile(join(PATH, 'uploads/', filename)):
				return filename

	def _check(self, cursor):
		return not self.is_uploaded(cursor)

	def _send_db(self, cursor):
		self.file.save(join(PATH, 'uploads', self.filename))
		cursor.add(req.add_picture(), (self.team_id, self.objective_id, self.filename, 0))

class PictureModel(Picture, Model):
	""" un squelette d'image avec une id """
	def __init__(self, team_id, objective_id, filename, status):
		super().__init__(team_id, objective_id)
		self.filename = filename
		self.status = status

class PictureOfTeam(PictureModel):
	""" recupere l'image de la team pour l'objectif specifie """
	def __init__(self, cursor, team_id, objective_id):
		self.cursor = cursor
		filename, status = self.__get_info(team_id, objective_id)
		super().__init__(team_id, objective_id, filename, status)

	def __get_info(self, team_id, objective_id):
		""" trouve le nom et le status de l'image """
		pic = self.cursor.get_one(req.picture_of_team(), (team_id, objective_id))
		return pic['filename'], pic['status']

class DeletePictureVue(Picture, Vue):
	""" suppression d'une picture """
	def _check(self, cursor):
		is_uploaded = self.is_uploaded(cursor)
		cursor.add_msg_if_false(is_uploaded, 'this picture is not uploaded')
		return is_uploaded

	def _send_db(self, cursor):
		cursor.add(req.delete_picture(), (self.team_id, self.objective_id))

class AcceptPictureVue(Picture, Vue):
	""" acceptation d'une image depuis la vue (par un admin) """
	def _check(self, cursor):
		return self.is_uploaded(cursor)

	def _send_db(self, cursor):
		cursor.add(req.accept_picture(), (self.team_id, self.objective_id))
