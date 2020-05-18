
from objects.jsonable import Vue, Model
from objects.teammate import TeammateVue
import model.requests as req
import colors

class NoTeamError(Exception):
	""" une exception si on ne trouve pas de team """

class Team:
	def __init__(self, name, color):
		self.name = name
		self.color = colors.Color(color)

class TeamModel(Team, Model):
	def __init__(self, cursor, team_id, team_name, color, points):
		super().__init__(team_name, color)
		self.cursor = cursor
		self.team_id = team_id
		self.points = points

	def _load_points(self, cursor, team_id):
		objs_points = cursor.get_one(req.get_team_points_from_objs(), (team_id,))['points']
		qrs_points = cursor.get_one(req.get_team_points_from_qrs(), (team_id,))['points']
		total = 0
		total += objs_points if objs_points is not None else 0 
		total += qrs_points if qrs_points is not None else 0 
		return total

class TeamModelFromId(TeamModel):
	def __init__(self, cursor, team_id):
		name, color = self.__load(cursor, team_id)
		super().__init__(cursor, team_id, name, color, self._load_points(cursor, team_id))

	def __load(self, cursor, team_id):
		req_res = cursor.get_one(req.team(), (team_id,))
		if req_res is None:
			raise NoTeamError('team {} does not exists'.format(team_id))
		return req_res['name'], req_res['color']

class TeamMedalModel(TeamModel):
	def __init__(self, cursor, team_id, team_name, color, points):
		super().__init__(cursor, team_id, team_name, color, points)
		self.medal = 4

	def set_medal(self, new_medal):
		self.medal = new_medal

	def get_medal(self):
		return self.medal

class TeamOf(TeamModel):
	def __init__(self, cursor, user_id):
		self.user_id = user_id
		team = cursor.get_one(req.team_of_user(), (user_id,))
		super().__init__(cursor, team['team_id'], team['name'], team['color'], self._load_points(cursor, team['team_id']))

class TeamVue(Team, Vue):
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

class RemoveTeamIfEmpty(Vue):
	def __init__(self, team_id):
		self.team_id = team_id

	def _check(self, cursor):
		return not cursor.get(req.users_of_team(), (self.team_id,))

	def _send_db(self, cursor):
		cursor.add(req.delete_team(), (self.team_id,))

class TeamsModel(Model):
	def __init__(self, cursor):
		self.cursor = cursor
		self.teams = self.__load_teams()
		self.teams = self.__load_medals()

	def __load_teams(self):
		res = []
		points_from_objs = {}
		for score in self.cursor.get(req.get_points_from_objs(), ()):
			points_from_objs[score['team_id']] = score['points']

		points_from_qrs = {}
		for score in self.cursor.get(req.get_points_from_qrs(), ()):
			points_from_qrs[score['team_id']] = score['points']

		for team in self.cursor.get(req.all_teams()):
			team_id = team['team_id']
			score = points_from_objs.pop(team_id, 0) + points_from_qrs.pop(team_id, 0)
			team = TeamMedalModel(self.cursor, team_id, team['name'], team['color'], score)
			res.append(team)
		return res

	def __load_medals(self):
		res = sorted(self.teams, key=lambda team: -team.points)
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
		return {team.team_id: team for team in self.teams}

class TeamLeave(Vue):
	def __init__(self, user_id):
		self.user_id = user_id

	def _check(self, cursor):
		return bool(cursor.get_one(req.team_of_user(), (self.user_id,)))

	def _send_db(self, cursor):
		team_id = cursor.get_one(req.team_of_user(), (self.user_id,))['team_id']
		cursor.add(req.leave_team(), (self.user_id,))
		RemoveTeamIfEmpty(team_id).send_db(cursor)
