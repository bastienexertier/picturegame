""" un module gerant les qr codes """

from random import choice
from string import ascii_lowercase
from os import remove
from os.path import isfile, join
from subprocess import check_output

from objects.jsonable import Vue, Model
import model.requests as req

class QRDoesntExistError(Exception):
	""" une exception si le qr n'existe pas """

class QRCode:
	""" un qr code """
	def __init__(self, points, description):
		self.points = points
		self.description = description

class QRCodeVue(QRCode, Vue):
	""" un qr code venant de la vue """
	def __create_key(self):
		while True:
			key = ''.join(choice(ascii_lowercase) for i in range(10))
			if not isfile(join('qrcodes', key + '.png')):
				return key

	def _check(self, cursor):
		""" verifie que le nombre de point sois correct, et que la descr soit assez longue """
		return self.points.isdigit() and len(self.description) > 3

	def _send_db(self, cursor):
		key = self.__create_key()
		filename = key + '.png'
		target_url = 'http://192.168.0.5:5000/qrcode/{}'.format(key)
		create_qrcode(target_url, join('qrcodes', filename))
		cursor.add(req.new_qr(), (key, self.points, self.description))

class RemoveQRCode(Vue):
	"""docstring for RemoveQRCode"""
	def __init__(self, key):
		self.key = key

	def _check(self, cursor):
		return True

	def _send_db(self, cursor):
		qrcode = QRCodeFromKey(cursor, self.key)
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
		qr = cursor.get_one(req.qr_from_key(), (key,))
		if qr is None:
			raise QRDoesntExistError(key)
		return qr['qr_id'], qr['points'], qr['description']

class QRCodesModel(Model):
	""" une liste de qr codes venant du model """
	def __init__(self, cursor):
		self.cursor = cursor
		self.qrcodes = self.__load_qrcodes()

	def __load_qrcodes(self):
		res = []
		for qrcode in self.cursor.get(req.all_qrcodes()):
			res.append(QRCodeModel(qrcode['points'], qrcode['description'], qrcode['qr_id'], qrcode['key']))
		return res

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
