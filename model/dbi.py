""" objet pour faiclement chopper un cursor """

import sqlite3 as sql
from model.db_init import DBNAME

def dict_factory(cursor, row):
	""" factory dictionnaire pour les lignes """
	res = {}
	for idx, col in enumerate(cursor.description):
		res[col[0]] = row[idx]
	return res

class Cursor:
	""" l'objet cursor supportant le context management """
	def __init__(self, *, do_print=None, show_msg=False):
		self.conn = None
		self.do_print = do_print
		self.show_msg = show_msg
		self.cursor = None
		self.msg = []

	# enter context

	def __enter__(self):
		self.conn = sql.connect(DBNAME)
		if self.do_print:
			self.conn.set_trace_callback(print)
		self.conn.row_factory = dict_factory

		self.cursor = self.conn.cursor()
		self.cursor.execute('PRAGMA foreign_keys = ON')
		return self

	# execute request

	def get(self, request, args=()):
		""" recupere toute les lignes correspondante a la requete """
		self.cursor.execute(request, args)
		return self.cursor.fetchall()

	def get_one(self, request, args=()):
		""" recupere une ligne correspondant a la requete """
		self.cursor.execute(request, args)
		return self.cursor.fetchone()

	def add(self, request, args=()):
		""" insere la ligne dans la bd """
		self.cursor.execute(request, args)
		return self.cursor.lastrowid

	# log messages

	def add_msg(self, msg):
		""" ajoute un msg a la pile de msg """
		self.msg.append(msg)

	def add_msg_if_true(self, flag, msg):
		""" ajoute un msg a la pile de msg ssi flag est true """
		if flag:
			self.add_msg(msg)

	def add_msg_if_false(self, flag, msg):
		""" ajoute un msg a la pile de msg ssi flag est false """
		if not flag:
			self.add_msg(msg)

	# exit context

	def __exit__(self, exc_type, exc_value, traceback):
		if self.msg and self.show_msg:
			print('\n'.join(self.msg))
		if exc_type is None:
			self.conn.commit()
		else:
			print(traceback)
			raise exc_type()
		self.conn.close()
		if isinstance(exc_type, sql.IntegrityError):
			print('sql IntegrityError')
			print(exc_value)
		return True
