""" setup du serveur """

import os
from path import PATH
import model.db_init

def create_folder_if_doesnt_exit(path, foldername):
	""" cree le dossier si il n'existe pas deja """
	full_path = path + foldername
	if not os.path.isdir(full_path):
		print('* {} doesnt exist'.format(full_path))
		os.mkdir(full_path)
		print('* {} created'.format(full_path))
	else:
		print('* {} already exists'.format(full_path))

def main():
	""" main """
	create_folder_if_doesnt_exit(PATH, 'uploads')
	create_folder_if_doesnt_exit(PATH, 'qrcodes')
	if not os.path.isfile(model.db_init.DBNAME):
		print('* database doesnt exist')
		model.db_init.main()
		print('* database initialized')
	else:
		print('* database already exists')

if __name__ == '__main__':
	main()
