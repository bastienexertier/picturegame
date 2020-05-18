
from objects.user import *
from objects.team import *
from model.dbi import Cursor

with Cursor(do_print=True) as cursor:
	UserVue('Bastien').send_db(cursor)
	bastien_id = cursor.cursor.lastrowid+1
	print(UserModel(cursor, bastien_id).json())
	TeamVue(bastien_id, 'Les totos').send_db(cursor)

