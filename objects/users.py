""" module gerant les listes d'users """

# pylint: disable=too-few-public-methods

from objects.jsonable import Model
from objects.user import UserModel
import model.requests as req

class UsersModel(Model):
	""" une classe contenant une liste de joueurs """
	def __init__(self, users):
		self.users = users

	@staticmethod
	def _get_users(cursor, request, args=()):
		req_res = cursor.get(request, args)
		return [UserModel(user['user_id'], user['name']) for user in req_res]

	def to_sorted(self):
		""" retourne la liste des users triee par nom """
		return sorted(self.users, key=lambda user: user.name)

	def nb_of_players(self):
		""" returns the number of players """
		return len(self.users)

class AllUsers(UsersModel):
	""" une classe contenant la liste de tous les joueurs """
	def __init__(self, cursor):
		super().__init__(UsersModel._get_users(cursor, req.users()))

class UsersFromTeam(UsersModel):
	""" une liste de tous les user d'une team """
	def __init__(self, cursor, team_id):
		super().__init__(UsersModel._get_users(cursor, req.users_of_team(), (team_id,)))
