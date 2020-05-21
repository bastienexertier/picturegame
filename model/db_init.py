""" initialisation de la db """

import sqlite3 as sql

from path import PATH

DBNAME = PATH + 'model/test.db'
SQLINIT = PATH + 'model/tables.sql'

def main():
	""" drop toutes les tables et les recree """
	with open(SQLINIT, 'r') as f_sql:
		script = f_sql.read()
	with sql.connect(DBNAME) as conn:
		cursor = conn.cursor()
		cursor.executescript(script)
		conn.commit()
	print(' * Created database {}'.format(DBNAME))

if __name__ == '__main__':
	main()
