""" model.qrcode """

from random import choice
from string import ascii_lowercase
from subprocess import check_output
from os import remove
from os.path import join, isfile

from model import db
from path import PATH, URL
from sqlalchemy import event

# pylint: disable=no-member

def qr_key():
	return ''.join(choice(ascii_lowercase) for i in range(10))

class QRCode(db.Model):
	""" a qrcode """
	id = db.Column(db.String, primary_key=True, default=qr_key)
	points = db.Column(db.Integer, nullable=False)
	description = db.Column(db.String, nullable=False)

	def __repr__(self):
		return f'<QRCode "{self.id}" - "{self.description}" for {self.points} points>'

class FoundQR(db.Model):
	""" a qrcode found by a team """
	team_id = db.Column(db.Integer, db.ForeignKey('team.id'), primary_key=True)
	qr_id = db.Column(db.String, db.ForeignKey('qr_code.id'), primary_key=True)

	qr = db.relationship('QRCode', backref=db.backref('teams', cascade='all, delete'))

	def __repr__(self):
		return f'<FoundQR {self.team.name} found {self.qr}>'

# =========================== QRCODE EVENT LISTENERS ===========================

@event.listens_for(QRCode, 'after_insert')
def create_qrcode(mapper, connection, target):
	""" cree et sauve un qrcode """
	cmd = f'qr "{URL}qrcodes/{target.id}" > {PATH}qrcodes/{target.id}.png'
	return check_output(cmd, shell=True)

@event.listens_for(QRCode, 'after_delete')
def delete_qrcode(mapper, connection, target):
	""" supprime le fichier d'un qrcode """
	if isfile(file := join(PATH, 'qrcodes', target.id + '.png')):
		remove(file)
