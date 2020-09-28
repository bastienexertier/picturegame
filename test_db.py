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

# A = User(name='A')
# B = User(name='B')
# totos = Team(name='totos', owner=A, color=1)
# totos.users.append(A)
# totos.users.append(B)
# db.session.add(totos)
# db.session.commit()

obj1 = Objective(points=50, description='Le premier objectif')
obj2 = Objective(points=50, description='Le deuxieme objectif')
# pic = Picture(objective=obj1, filename='umhquypwri.jpg', status=1, team=totos)

# db.session.add(pic)
db.session.add(obj1)
db.session.add(obj2)
db.session.commit()

qrcode1 = QRCode(id='abcdef', points=30, description='Le premier qrcode')
qrcode2 = QRCode(id='abcdeg', points=30, description='Le deuxieme qrcode')
# found = FoundQR(qr=qrcode1, team=totos)

# db.session.add(found)
db.session.add(qrcode1)
db.session.add(qrcode2)
db.session.commit()
