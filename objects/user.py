""" module gerant les users """

# pylint: disable=too-few-public-methods

from objects.jsonable import Vue, Model
import model.requests as req

class NoUserError(Exception):
	""" une erreur si l'utilisateur n'est pas defini cote client """

class User:
	""" un squelette d'user, avec seulement un nom """
	def __init__(self, name):
		self.name = name

class UserVue(User, Vue):
	""" un user cree depuis la vue """
	def _check(self, cursor):
		res = cursor.get(req.user_with_name(), (self.name,))
		cursor.add_msg_if_true(res, 'another user already has this name')
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

	def __get_name(self, user_id):
		req_res = self.cursor.get_one(req.user(), (user_id,))
		if not req_res:
			raise NoUserError()
		return req_res['name']

class RemoveUser(Vue):
	""" supprime un user de la db en fct de son id """
	def __init__(self, user_id):
		self.user_id = user_id

	def _check(self, cursor):
		user_exists = bool(cursor.get_one(req.user(), (self.user_id,)))
		cursor.add_msg_if_false(user_exists, 'this user doesnt exist and cant be removed')
		return user_exists

	def _send_db(self, cursor):
		cursor.add(req.delete_user(), (self.user_id,))
