""" module gerant les listes de qrcodes """

# pylint: disable=too-few-public-methods

from objects.jsonable import Model
from objects.qrcode import QRCodeModel
import model.requests as req

class QRCodesModel(Model):
	""" une liste de qr codes venant du model """
	def __init__(self, cursor):
		self.qrcodes = self._load_qrcodes(cursor)

	def _load_qrcodes(self, cursor):
		raise NotImplementedError()

	def to_dict(self):
		""" retourne les qrs sous forme de dict(qr_id) = qr """
		return {qr.qr_id: qr for qr in self.qrcodes}

class AllQRCodesModel(QRCodesModel):
	""" tous les qrcodes de la db """
	def _load_qrcodes(self, cursor):
		res = []
		for qrcode in cursor.get(req.all_qrcodes()):
			res.append(QRCodeModel(qrcode['points'], qrcode['description'], qrcode['qr_id'], qrcode['key']))
		return res

class QRCodesOfTeam(QRCodesModel):
	""" tous les qr codes trouve par une equipe """
	def __init__(self, cursor, team_id):
		self.team_id = team_id
		super().__init__(cursor)

	def _load_qrcodes(self, cursor):
		res = []
		for qrcode in cursor.get(req.all_qr_found_by_team(), (self.team_id,)):
			res.append(QRCodeModel(qrcode['points'], qrcode['description'], qrcode['qr_id'], qrcode['key']))
		return res
