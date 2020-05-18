""" une classe de couleurs """

COLORS = [
    ['#6D214F', '#B33771'],
    ['#006400', '#008000'],
    ['#182C61', '#3B3B98'],
    ['#5758BB', '#7B68EE'],
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
