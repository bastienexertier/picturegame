""" model.user """

from model import db

# pylint: disable=no-member

class User(db.Model):
	""" a user """
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(), nullable=False, unique=True)
	team = db.relationship('Team', backref=db.backref('users', uselist=True))

	def __repr__(self):
		return f'<User {self.name} in {self.team.name if self.team else None}>'

class Team(db.Model):
	""" a team """
	id = db.Column(db.Integer, primary_key=True)
	owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	name = db.Column(db.String(), nullable=False, unique=True)
	color = db.Column(db.Integer, nullable=False)

	owner = db.relationship('User', cascade='all,delete')

	def __repr__(self):
		return f'<Team {self.name}, owner {self.owner.name}, color {self.color}>'
