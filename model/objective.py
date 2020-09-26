""" model.objective """

from model import db

# pylint: disable=no-member

class Objective(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	points = db.Column(db.Integer, nullable=False)
	description = db.Column(db.String, nullable=False)

	def __repr__(self):
		return f'<Objective "{self.description}" for {self.points} points>'

class Picture(db.Model):
	team_id = db.Column(db.Integer, db.ForeignKey('team.id'), primary_key=True)
	objective_id = db.Column(db.Integer, db.ForeignKey('objective.id'), primary_key=True)

	filename = db.Column(db.String, nullable=False)
	status = db.Column(db.Integer, nullable=False)

	team = db.relationship('Team', cascade='all,delete')
	objective = db.relationship('Objective', cascade='all,delete')

	team = db.relationship('Team', backref=db.backref('pictures', cascade='all, delete'))
	objective = db.relationship('Objective', backref=db.backref('teams', cascade='all, delete'))

	def __repr__(self):
		return f'<Picture for {self.objective} by {self.team.name}>'
