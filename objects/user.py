
from objects.jsonable import Vue, Model
import model.requests as req

class User:
	def __init__(self, name):
		self.name = name

class UserVue(User, Vue):
	def _check(self, cursor):
		res = cursor.get(req.user_with_name(), (self.name,))
		return not res

	def _send_db(self, cursor):
		cursor.add(req.new_user(), (self.name,))

class UserModel(User, Model):
	def __init__(self, cursor, user_id):
		self.cursor = cursor
		self.user_id = user_id
		super().__init__(self.__get_name())

	def json(self):
		return self.name

	def __get_name(self):
		return self.cursor.get_one(req.user(), (self.user_id,))['name']

class Teammate:
	def __init__(self, user_id, team_id, status):
		self.user_id = user_id
		self.team_id = team_id
		self.status = status

	def __repr__(self):
		temp = 'user_id:{}, team_id:{}, status:{}'
		return temp.format(self.user_id, self.team_id, self.status)

class TeammateVue(Teammate, Vue):
	def __init__(self, user_id, team_id, status):
		super().__init__(user_id, team_id, status)

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

class Teammates(Model):
	def __init__(self, cursor, team_id):
		self.cursor = cursor
		self.team_id = team_id
		self.teammates = self.__load_teammates()

	def __load_teammates(self):
		res = []
		for user in self.cursor.get(req.users_of_team(), (self.team_id,)):
			res.append(User(user['name']))
		return res
