""" model.user """

from model import db, ma
from colors import get_color
from model.qrcode import FoundQRSchema
from model.objective import PictureSchema

# pylint: disable=no-member

class User(db.Model):
	""" a user """
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(), nullable=False, unique=True)

	team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
	team = db.relationship(
		'Team',
		backref=db.backref('users', uselist=True),
		uselist=False,
		foreign_keys=team_id,
		post_update=True
	)

	def __repr__(self):
		return f'<User {self.name} in {self.team.name if self.team else None}>'

class Team(db.Model):
	""" a team """
	id = db.Column(db.Integer, primary_key=True)
	owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	name = db.Column(db.String(), nullable=False, unique=True)
	color = db.Column(db.Integer, nullable=False)

	owner = db.relationship('User', foreign_keys=owner_id)
	# l'objet users utilise la reference owner_id alors qu'il ne devrait pas!!

	qrs = db.relationship('FoundQR', backref='team', cascade='all, delete')
	pictures = db.relationship('Picture', backref='team', cascade='all, delete')

	def __repr__(self):
		return f'<Team {self.name}, owner {self.owner.name}, color {self.color}>'

# =================================== SCHEMA ===================================

class UserSchema(ma.Schema):
	""" un schema user """
	class Meta:
		model = User
		fields = ('id', 'name')

class TeamSchema(ma.Schema):
	""" team schema """
	class Meta:
		model = Team
		fields = ('id', 'owner', 'name', 'colors', 'score')
	colors = ma.Function(lambda team: get_color(team.color))
	owner = ma.Nested(UserSchema)
	score = ma.Method('compute_score')

	def compute_score(self, team):
		"""" retourne le score de l'equipe """
		return (
			sum(map(lambda pic: pic.objective.points, team.pictures)) +
			sum(map(lambda found: found.qr.points, team.qrs))
		)

	def dump(self, element):
		res = super().dump(element)
		if self.many:
			res.sort(key=lambda t: -t['score'])
		return res

class TeamFullSchema(TeamSchema):
	""" un schema de team avec les users """
	class Meta:
		model = Team
		fields = ('id', 'owner', 'name', 'colors', 'score', 'users', 'qrs', 'pictures')
	users = ma.Nested(UserSchema, many=True)
	pictures = ma.Nested(PictureSchema, many=True)
	qrs = ma.Pluck(FoundQRSchema, 'qr', many=True)

def load_medals(teams):
	""" modifie les medailles """
	res = sorted(teams, key=lambda team: -team['score'])
	scores = {}
	for team in res:
		if team['score'] not in scores:
			scores[team['score']] = []
		scores[team['score']].append(team)
	current_medal = 1
	for score in reversed(sorted(scores.keys())):
		current_medal += len(scores[score]) - 1
		if current_medal > 3:
			break
		for team in scores[score]:
			team['medal'] = current_medal
		current_medal += 1
	return teams
