""" une classe de couleurs """

COLORS = [
    ['#801336', '#c72c41'],
    ['#06623b', '#649d66'],
    ['#151965', '#32407b'],
    ['#45046a', '#5c2a9d'],
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
		self.color_id = color_id%len(COLORS)
		self.colors = COLORS[self.color_id]
