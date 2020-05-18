""" module gerant les objets equipes """

from itertools import chain

from objects.jsonable import Vue, Model
from objects.teammate import TeammateVue
import model.requests as req
import colors

class NoTeamError(Exception):
	""" une exception si on ne trouve pas de team """

class Team:
	""" une equipe basique """
	def __init__(self, name, color):
		self.name = name
		self.color = colors.Color(color)

class TeamModel(Team, Model):
	""" une equipe venant du model """
	def __init__(self, cursor, team_id, team_name, color, points):
		super().__init__(team_name, color)
		self.cursor = cursor
		self.team_id = team_id
		self.points = points

	@staticmethod
	def _load_points(cursor, team_id):
		objs_points = cursor.get_one(req.get_team_points_from_objs(), (team_id,))
		qrs_points = cursor.get_one(req.get_team_points_from_qrs(), (team_id,))
		return objs_points.pop('points', 0) + qrs_points.pop('points', 0)

class TeamModelFromId(TeamModel):
	""" une equipe a partir d'une id de team """
	def __init__(self, cursor, team_id):
		name, color = TeamModelFromId.__load(cursor, team_id)
		points = TeamModel._load_points(cursor, team_id)
		super().__init__(cursor, team_id, name, color, points)

	@staticmethod
	def __load(cursor, team_id):
		req_res = cursor.get_one(req.team(), (team_id,))
		if req_res is None:
			raise NoTeamError('team {} does not exists'.format(team_id))
		return req_res['name'], req_res['color']

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
		team_id = cursor.get_one(req.team_of_user(), (user_id,))['team_id']
		super().__init__(cursor, team_id)

class TeamVue(Team, Vue):
	""" une equipe venant de la vue, envoie dans la bd apres verif """
	def __init__(self, user_id, team_name, color):
		super().__init__(team_name, color)
		self.user_id = user_id

	def _check(self, cursor):
		same_name = cursor.get(req.team_with_name(), (self.name,))
		user_team = cursor.get(req.team_id_of_user(), (self.user_id,))
		if same_name:
			cursor.add_msg('same name')
		if user_team:
			cursor.add_msg('user has already a team')
		return not same_name and not user_team

	def _send_db(self, cursor):
		team_id = cursor.add(req.new_team(), (self.name, self.color.color_id))
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
			score = points.pop(team_id, 0)
			res.append(TeamMedalModel(cursor, team_id, team['name'], team['color'], score))
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

class TeamLeave(Vue):
	""" represente un user qui quitte son equipe, l'equipe est detruite si vide """
	def __init__(self, user_id):
		self.user_id = user_id
		self.team_id = None

	def _check(self, cursor):
		self.team_id = cursor.get_one(req.team_of_user(), (self.user_id,))['team_id']
		return bool(self.team_id)

	def _send_db(self, cursor):
		cursor.add(req.leave_team(), (self.user_id,))
		RemoveTeamIfEmpty(self.team_id).send_db(cursor)

class RemoveTeamIfEmpty(Vue):
	""" suppression de l'equipe si elle est vide """
	def __init__(self, team_id):
		self.team_id = team_id

	def _check(self, cursor):
		""" verifie que l'equipe soit bien vide """
		return not cursor.get(req.users_of_team(), (self.team_id,))

	def _send_db(self, cursor):
		cursor.add(req.delete_team(), (self.team_id,))
