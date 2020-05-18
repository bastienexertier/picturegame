""" une classe de couleurs """

COLORS = [
    ['#EA2027', '#EE5A24'],
    ['#006266', '#009432'],
    ['#1B1464', '#0652DD'],
    ['#5758BB', '#9980FA'],
    ['#6F1E51', '#833471'],
]

class Colors:
	""" un ensemble de couleurs """
	def __init__(self):
		self.colors = []
		for idx in range(len(COLORS)):
			self.colors.append(Color(idx))

class Color:
	""" un objet couleur a partir d'une id """
	def __init__(self, color_id):
		self.color_id = color_id%7
		self.colors = COLORS[self.color_id]
