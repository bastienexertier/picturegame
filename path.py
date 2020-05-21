""" path du jeu """

import os

if 'PICTUREGAMEPATH' not in os.environ:
	print('Please set your PICTUREGAMEPATH variable')
	exit(0)

PATH = os.environ['PICTUREGAMEPATH']

if 'PICTUREGAMEURL' not in os.environ:
	print('Please set your PICTUREGAMEURL variable')
	exit(0)

URL = os.environ['PICTUREGAMEURL']
