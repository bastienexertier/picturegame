""" Un object model qui doit iplem .json() et Vue qui doit implem ._check et ._send_db """

from sqlite3 import IntegrityError

class Model:
	""" une classe abstraite pour les objs venant de la bd """

class Vue:
	""" une classe abstraire pour les objets a verifier, et envoyer dans la db """
	def _check(self, cursor):
		""" verifie si l'objet est valide pour l'envoi en db """
		return True

	def _send_db(self, cursor):
		""" envoie l'objet en db """
		raise NotImplementedError('must override')

	def send_db(self, cursor):
		""" envoie l'objet en db apres verification """
		valid = self._check(cursor)
		if valid:
			try:
				self._send_db(cursor)
			except IntegrityError:
				valid = False
		return valid
