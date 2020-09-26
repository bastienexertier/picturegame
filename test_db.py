""" test du model sqlalchemy """

# pylint: disable=no-member

from app import app
from model import db
from model.user import User, Team
from model.qrcode import QRCode, FoundQR
from model.objective import Objective, Picture

db.init_app(app)
app.app_context().push()

db.drop_all()
db.session.commit()
db.create_all()
print('ok')

toto = User(name='toto')
totos = Team(name='totos', owner=toto, color=1)
totos.users.append(toto)
db.session.add(totos)
db.session.commit()
print('toto, totos in the db')

obj = Objective(points=50, description='Le premier objectif')
pic = Picture(team=totos, objective=obj, filename='0.png', status=1)

db.session.add(pic)
db.session.commit()

qrcode = QRCode(id='abcdef', points=30, description='Le premier qrcode')
found = FoundQR(qr=qrcode, team=totos)

db.session.add(found)
db.session.commit()
