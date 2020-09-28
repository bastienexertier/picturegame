""" setup du serveur """

import os
from path import PATH
from model.db_init import db_init_main, DBNAME

def create_folder_if_doesnt_exit(path, foldername):
	""" cree le dossier si il n'existe pas deja """
	full_path = path + foldername
	if not os.path.isdir(full_path):
		print(' * {} doesnt exist'.format(full_path))
		os.mkdir(full_path)
		print(' * {} created'.format(full_path))
	else:
		print(' * {} already exists'.format(full_path))

def main(app, db):
	""" main """
	create_folder_if_doesnt_exit(PATH, 'uploads')
	create_folder_if_doesnt_exit(PATH, 'qrcodes')
	db.init_app(app)
	if not os.path.isfile(DBNAME):
		print(' * database doesnt exist')
		db_init_main(app, db)
		print(' * database initialized')
	else:
		print(' * database already exists')

if __name__ == '__main__':
	main()
