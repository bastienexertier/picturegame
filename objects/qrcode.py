""" un module gerant les qr codes """

from random import choice
from string import ascii_lowercase
from os.path import isfile, join
from subprocess import check_output

from objects.jsonable import Vue, Model
import model.requests as req

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
		print(create_qrcode(target_url, join('qrcodes', filename)))
		cursor.add(req.new_qr(), (key, self.points, self.description))

class QRCodeModel(QRCode, Model):
	""" un qrcode venant du model """
	def __init__(self, points, description, key):
		super().__init__(points, description)
		self.key = key

class QRCodesModel(Model):
	""" une liste de qr codes venant du model """
	def __init__(self, cursor):
		self.cursor = cursor
		self.qrcodes = self.__load_qrcodes()

	def __load_qrcodes(self):
		res = []
		for qrcode in self.cursor.get(req.all_qrcodes()):
			res.append(QRCodeModel(qrcode['points'], qrcode['description'], qrcode['key']))
		return res


def create_qrcode(data, filename):
	""" cree et sauve un qrcode """
	cmd = 'qr "{}" > {}'.format(data, filename)
	# ne depend pas d'entree user donc shell=True est ok
	return check_output(cmd, shell=True)
