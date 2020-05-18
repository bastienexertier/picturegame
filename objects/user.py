
from objects.jsonable import Vue, Model
from objects.team import TeamLeave
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
	""" squelette d'un user model """
	def __init__(self, user_id, name):
		super().__init__(name)
		self.user_id = user_id

class UserModelName(UserModel):
	""" un user ou on charge le nom depuis la db """
	def __init__(self, cursor, user_id):
		self.cursor = cursor
		super().__init__(user_id, self.__get_name(user_id))

	def json(self):
		return self.name

	def __get_name(self, user_id):
		return self.cursor.get_one(req.user(), (user_id,))['name']

class RemoveUser(Vue):
	""" supprime un user de la db en fct de son id """
	def __init__(self, user_id):
		self.user_id = user_id

	def _check(self, cursor):
		return bool(cursor.get_one(req.user(), (self.user_id,)))

	def _send_db(self, cursor):
		TeamLeave(self.user_id).send_db(cursor)
		cursor.add(req.delete_user(), (self.user_id,))

class UsersModel(Model):
	""" une classe contenant la liste des joueurs """
	def __init__(self, cursor):
		self.users = UsersModel.__get_users(cursor)

	@staticmethod
	def __get_users(cursor):
		return [UserModel(user['user_id'], user['name']) for user in cursor.get(req.users())]

class UsersFromTeam(UsersModel):
	def __init__(self, cursor, team_id):
		self.cursor = cursor
		self.team_id = team_id
		self.users = self.__load()

	def __load(self):
		res = []
		for user in self.cursor.get(req.users_of_team(), (self.team_id,)):
			res.append(User(user['name']))
		return res
