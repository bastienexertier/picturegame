""" module gerant les objets equipes """

# pylint: disable=too-few-public-methods

from itertools import chain

from objects.jsonable import Vue, Model
from objects.teammate import TeammateVue
from objects.users import UsersFromTeam
import model.requests as req
import colors

class NoTeamError(Exception):
	""" une exception si on ne trouve pas de team """

class Team:
	""" une equipe basique """
	def __init__(self, name, color, owner):
		self.name = name
		self.color = colors.Color(color)
		self.owner = owner

	def is_owned_by(self, user_id):
		""" retourn vrai si l'id donne est celle de l'owner """
		return self.owner == user_id

class TeamModel(Team, Model):
	""" une equipe venant du model """
	def __init__(self, cursor, team_id, points, *args):
		super().__init__(*args)
		self.cursor = cursor
		self.team_id = team_id
		self.points = points

	@staticmethod
	def _load_points(cursor, team_id):
		objs_points = cursor.get_one(req.get_team_points_from_objs(), (team_id,))
		qrs_points = cursor.get_one(req.get_team_points_from_qrs(), (team_id,))

		total = 0
		if objs_points:
			total += objs_points.pop('points', 0)
		if qrs_points:
			total += qrs_points.pop('points', 0)
		return total

class TeamModelFromId(TeamModel):
	""" une equipe a partir d'une id de team """
	def __init__(self, cursor, team_id):
		args = TeamModelFromId.__load(cursor, team_id)
		points = TeamModel._load_points(cursor, team_id)
		super().__init__(cursor, team_id, points, *args)

	@staticmethod
	def __load(cursor, team_id):
		req_res = cursor.get_one(req.team(), (team_id,))
		if req_res is None:
			raise NoTeamError('team {} does not exists'.format(team_id))
		return req_res['name'], req_res['color'], req_res['owner_id']

class TeamMedalModel(TeamModel):
	""" une Team avec un attribut medaille, connait deja son nombre de points """
	def __init__(self, *args):
		super().__init__(*args)
		self.medal = 4

	def set_medal(self, new_medal):
		""" set la medaille """
		self.medal = new_medal

class TeamOf(TeamModelFromId):
	""" represente l'equipe d'un user """
	def __init__(self, cursor, user_id):
		self.user_id = user_id
		team = cursor.get_one(req.team_of_user(), (user_id,))
		if not team:
			raise NoTeamError()
		super().__init__(cursor, team['team_id'])

class TeamVue(Team, Vue):
	""" une equipe venant de la vue, envoie dans la bd apres verif """
	def __init__(self, user_id, team_name, color):
		super().__init__(team_name, color, user_id)
		self.user_id = user_id

	def _check(self, cursor):
		same_name = cursor.get(req.team_with_name(), (self.name,))
		user_has_team = cursor.get(req.team_id_of_user(), (self.user_id,))
		cursor.add_msg_if_true(same_name, 'same name')
		cursor.add_msg_if_true(user_has_team, 'user has already a team')
		return not same_name and not user_has_team

	def _send_db(self, cursor):
		team_id = cursor.add(req.new_team(), (self.name, self.color.color_id, self.user_id))
		TeammateVue(self.user_id, team_id, 5).send_db(cursor)

class TeamsModel(Model):
	""" une list de team venant du model, calcul les points et les medailles """
	def __init__(self, cursor):
		self.teams = TeamsModel.__load_teams(cursor)
		self.teams = TeamsModel.__load_medals(self.teams)

	@staticmethod
	def __load_points(cursor):
		objs_pts = cursor.get(req.get_points_from_objs())
		qrs_pts = cursor.get(req.get_points_from_qrs())

		res = {}
		for pts in chain(objs_pts, qrs_pts):
			team_id = pts['team_id']
			if team_id not in res:
				res[team_id] = 0
			res[team_id] += pts['points']

		return res

	@staticmethod
	def __load_teams(cursor):
		""" charge les points des equipes """
		res = []
		points = TeamsModel.__load_points(cursor)

		for team in cursor.get(req.all_teams()):
			team_id = team['team_id']
			team_attrs = team['name'], team['color'], team['owner_id']
			score = points.pop(team_id, 0)
			res.append(TeamMedalModel(cursor, team_id, score, *team_attrs))
		return res

	@staticmethod
	def __load_medals(teams):
		""" modifie les medailles """
		res = sorted(teams, key=lambda team: -team.points)
		scores = {}
		for team in res:
			if team.points not in scores:
				scores[team.points] = []
			scores[team.points].append(team)
		current_medal = 1
		for score in reversed(sorted(scores.keys())):
			current_medal += len(scores[score]) - 1
			if current_medal > 3:
				break
			for team in scores[score]:
				team.set_medal(current_medal)
			current_medal += 1
		return res

	def to_dict(self):
		""" retourne la liste de team sous forme de dict(team_id) = team """
		return {team.team_id: team for team in self.teams}

	def owners(self):
		""" retourne un dict d'id de users qui sont des owners de team """
		return {team.owner: team for team in self.teams}

class TeamLeave(Vue):
	""" represente un user qui quitte son equipe, l'equipe est detruite si vide """
	def __init__(self, user_id):
		self.user_id = user_id
		self.team = None

	def _check(self, cursor):
		""" verifie que l'utilisateur a bien une tea, qu'il peut leave """
		try:
			self.team = TeamOf(cursor, self.user_id)

			nb_of_teammates = UsersFromTeam(cursor, self.team.team_id).nb_of_players()
			is_owner = self.team.is_owned_by(self.user_id)
			can_leave = not (is_owner and (nb_of_teammates > 1))

			cursor.add_msg_if_false(can_leave, 'user is owner of team and cant leave')
			return can_leave
		except NoTeamError:
			cursor.add_msg('user doesnt have a team to leave')
			return False

	def _send_db(self, cursor):
		cursor.add(req.leave_team(), (self.user_id,))
		RemoveTeamIfEmpty(self.team.team_id).send_db(cursor)

class RemoveTeamIfEmpty(Vue):
	""" suppression de l'equipe si elle est vide """
	def __init__(self, team_id):
		self.team_id = team_id

	def _check(self, cursor):
		""" verifie que l'equipe soit bien vide """
		return not cursor.get(req.users_of_team(), (self.team_id,))

	def _send_db(self, cursor):
		cursor.add(req.delete_team(), (self.team_id,))

class ChangeOwner(Vue):
	""" change l'owner d'une team """
	def __init__(self, team_id, new_owner):
		self.team_id = team_id
		self.new_owner = new_owner

	def _send_db(self, cursor):
		cursor.add(req.change_owner(), (self.new_owner, self.team_id))
