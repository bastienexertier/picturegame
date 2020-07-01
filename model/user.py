""" model.user """

from model import db

class User(db.Model):
	__tablename__ = 'users'
	user_id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(), nullable=False, unique=True)
