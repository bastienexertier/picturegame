from flask_sqlalchemy import SQLAlchemy, event
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow(db)

def init_app(app):
	""" initialise l'app avec le model """
	app.app_context().push()
	db.init_app(app)
	event.listen(db.engine, 'connect', lambda con, _: con.execute('pragma foreign_keys=ON'))

	db.create_all()
	db.session.commit()
