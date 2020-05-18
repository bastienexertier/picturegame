
from objects.jsonable import Vue, Model

import model.requests as req

class Teammate:
	def __init__(self, user_id, team_id, status):
		self.user_id = user_id
		self.team_id = team_id
		self.status = status

	def __repr__(self):
		temp = 'user_id:{}, team_id:{}, status:{}'
		return temp.format(self.user_id, self.team_id, self.status)

class TeammateVue(Teammate, Vue):
	""" un user a choisi une equipe """
	def _check(self, cursor):
		return True

	def _send_db(self, cursor):
		cursor.add(req.add_teammate(), (self.team_id, self.user_id, self.status))

class TeammateModel(Teammate, Model):
	def __init__(self, cursor, user_id):
		self.cursor = cursor
		team_id, status = self.__load_team(user_id)
		super().__init__(user_id, team_id, status)

	def __load_team(self, user_id):
		req_res = self.cursor.get_one(req.team_id_of_user(), (user_id,))
		if req_res:
			return req_res['team_id'], req_res['status']
		return None, None
