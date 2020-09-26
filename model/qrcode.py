""" model.qrcode """

from model import db

# pylint: disable=no-member

class QRCode(db.Model):
	""" a qrcode """
	id = db.Column(db.String, primary_key=True)
	points = db.Column(db.Integer, nullable=False)
	description = db.Column(db.String, nullable=False)

	def __repr__(self):
		return f'<QRCode "{self.id}" - "{self.description}" for {self.points} points>'

class FoundQR(db.Model):
	""" a qrcode found by a team """
	team_id = db.Column(db.Integer, db.ForeignKey('team.id'), primary_key=True)
	qr_id = db.Column(db.String, db.ForeignKey('qr_code.id'), primary_key=True)

	team = db.relationship('Team', backref=db.backref('qrs', cascade='all, delete'))
	qr = db.relationship('QRCode', backref=db.backref('teams', cascade='all, delete'))

	def __repr__(self):
		return f'<FoundQR {self.team.name} found {self.qr}>'
