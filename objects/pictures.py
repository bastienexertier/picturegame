""" module gerant les listes d'images """

# pylint: disable=too-few-public-methods

from random import choice

from objects.jsonable import Model
from objects.picture import PictureModel
import model.requests as req

# =============================== ABSTRACT ====================================

class PicturesModel(Model):
	""" un dict d'images venant du model """
	def __init__(self, pictures):
		self.pictures = pictures

	@staticmethod
	def _load_pictures(cursor, request, args):
		""" genere le dict a partir de la requete et args donnes """
		res = {}
		req_res = cursor.get(request, args)
		for pic in req_res:
			team_id = pic['team_id']
			if team_id not in res:
				res[team_id] = {}
			obj_id = pic['objective_id']
			infos = pic['filename'], pic['status']
			res[team_id][obj_id] = PictureModel(team_id, obj_id, *infos)
		return res

# ============================== IMPLEM =======================================

class PicturesOfTeamModel(PicturesModel):
	""" toutes les images d'une equipe """
	def __init__(self, cursor, team_id):
		load_req = req.get_team_pictures()
		every_pictures = PicturesModel._load_pictures(cursor, load_req, (team_id,))
		super().__init__(every_pictures.get(team_id, {}))

class AllPicturesModel(PicturesModel):
	""" toutes les images """
	def __init__(self, cursor):
		load_req = req.get_all_pictures()
		super().__init__(PicturesModel._load_pictures(cursor, load_req, ()))

	def random_picture(self):
		""" rend une image random """
		pic_list = []
		for team_pics in self.pictures.values():
			for pic in team_pics.values():
				pic_list.append(pic)
		return choice(pic_list) if pic_list else None

class PicturesWithStatus(PicturesModel):
	""" une classe pour aller chercher les images avec un certain status """
	def __init__(self, cursor, status):
		load_req = req.get_pictures_w_status()
		pictures = PicturesModel._load_pictures(cursor, load_req, (status,))
		super().__init__(pictures)
