""" un module gerant les qr codes """

# pylint: disable=too-few-public-methods

from random import choice
from string import ascii_lowercase
from os import remove
from os.path import join
from subprocess import check_output

from objects.jsonable import Vue, Model
import model.requests as req

TARGET_BASE_URL = 'http://192.168.0.5:5000'

class QRDoesntExistError(Exception):
	""" une exception si le qr n'existe pas """

class QRCode:
	""" un qr code """
	def __init__(self, points, description):
		self.points = points
		self.description = description

class QRCodeVue(QRCode, Vue):
	""" un qr code venant de la vue """
	@staticmethod
	def __create_key(cursor):
		""" genere une cle qui n'est pas deja utilisee """
		all_qrs = cursor.get(req.all_qrcodes())
		all_keys = map(lambda qr: qr['key'], all_qrs)
		while True:
			key = ''.join(choice(ascii_lowercase) for i in range(10))
			if key not in all_keys:
				return key

	def _check(self, cursor):
		""" verifie que le nombre de point sois correct, et que la descr soit assez longue """
		return self.points.isdigit() and len(self.description) > 3

	def _send_db(self, cursor):
		key = QRCodeVue.__create_key(cursor)
		filename = key + '.png'
		target_url = '{}/qrcode/{}'.format(TARGET_BASE_URL, key)
		create_qrcode(target_url, join('qrcodes', filename))
		cursor.add(req.new_qr(), (key, self.points, self.description))

class RemoveQRCode(Vue):
	"""docstring for RemoveQRCode"""
	def __init__(self, key):
		self.key = key

	def _check(self, cursor):
		qrcode = QRCodeFromKey(cursor, self.key)
		return bool(qrcode)

	def _send_db(self, cursor):
		cursor.add(req.delete_qr(), (self.key,))
		remove(join('qrcodes', self.key + '.png'))

class QRCodeModel(QRCode, Model):
	""" un qrcode venant du model """
	def __init__(self, points, description, qr_id, key):
		super().__init__(points, description)
		self.qr_id = qr_id
		self.key = key

class QRCodeFromKey(QRCodeModel):
	""" un qrcode a partir d'une key """
	def __init__(self, cursor, key):
		qr_id, points, description = QRCodeFromKey.__load(cursor, key)
		super().__init__(points, description, qr_id, key)

	@staticmethod
	def __load(cursor, key):
		""" charge le qrcode a partir de la cle """
		qrcode = cursor.get_one(req.qr_from_key(), (key,))
		if qrcode is None:
			raise QRDoesntExistError(key)
		return qrcode['qr_id'], qrcode['points'], qrcode['description']

class FoundQRCodeVue(Vue):
	""" object representant une equipe qui a trouve un qr """
	def __init__(self, team_id, qr_id):
		self.team_id = team_id
		self.qr_id = qr_id

	def _check(self, cursor):
		""" verifie si deja dans la db """
		return cursor.get_one(req.has_found_qr(), (self.team_id, self.qr_id)) is None

	def _send_db(self, cursor):
		cursor.add(req.found_qr(), (self.team_id, self.qr_id))

def create_qrcode(data, filename):
	""" cree et sauve un qrcode """
	cmd = 'qr "{}" > {}'.format(data, filename)
	# ne depend pas d'entree user donc shell=True est ok
	return check_output(cmd, shell=True)
