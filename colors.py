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
			self.colors.append(get_color(idx))

def get_color(color_id):
	""" retourne la couleur de la color_id """
	return COLORS[color_id%len(COLORS)]
