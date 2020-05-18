
class NoUserError(Exception):
	""" une erreur si l'utilisateur n'est pas defini cote client """

def user(session):
	""" retourne l'user_id si dans session, sinon exception """
	if 'user' not in session:
		raise NoUserError()
	return session['user']
