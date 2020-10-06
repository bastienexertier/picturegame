""" model.user """

from sqlalchemy import event

from model import db
from colors import get_color

# pylint: disable=no-member

class User(db.Model):
	""" a user """
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(), nullable=False, unique=True)

	team_id = db.Column(db.Integer, db.ForeignKey('team.id', use_alter=True))
	team = db.relationship(
		'Team',
		backref=db.backref('users', uselist=True),
		uselist=False,
		foreign_keys=team_id,
		post_update=True
	)
	comments = db.relationship('Comment', backref='user', cascade='all, delete')

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

@event.listens_for(Team, 'load')
def compute_score(target, context):
	"""" retourne le score de l'equipe """
	picture_score = sum(map(lambda pic: pic.objective.points, target.pictures))
	qr_score = sum(map(lambda found: found.qr.points, target.qrs))
	target.score = picture_score + qr_score

@event.listens_for(Team, 'load')
def add_colors(target, context):
	"""  """
	target.colors = get_color(target.color)

def load_medals(teams):
	""" modifie les medailles """
	res = sorted(teams, key=lambda team: -team.score)
	scores = {}
	for team in res:
		if team.score not in scores:
			scores[team.score] = []
		scores[team.score].append(team)
	current_medal = 1
	for score in reversed(sorted(scores.keys())):
		current_medal += len(scores[score]) - 1
		if current_medal > 3:
			break
		for team in scores[score]:
			team.medal = current_medal
		current_medal += 1
	return teams
