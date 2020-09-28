""" initialisation de la db """

import sqlite3 as sql

from path import PATH

DBNAME = PATH + 'model/test.db'

def db_init_main(app, db):
	""" drop toutes les tables et les recree """
	app.app_context().push()
	db.create_all()
	db.session.commit()
	print(' * Created database {}'.format(DBNAME))

if __name__ == '__main__':
	main()
