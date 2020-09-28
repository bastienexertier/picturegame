""" module contenant les tables pour les commentaires """

from model import db, ma

class Comment(db.Model):
	""" a qrcode """
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	picture_id = db.Column(db.Integer, db.ForeignKey('picture.id'))

	text = db.Column(db.String)

	def __repr__(self):
		return f'<Comment on {self.picture} by {self.user.name} : {self.text}>'

class CommentSchema(ma.Schema):
	class Meta:
		model = Comment
		fieds = ('id', 'user_id', 'user_name', 'text')
	user_name = ma.Function(lambda comment: comment.user.name)
