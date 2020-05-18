
from objects.jsonable import Vue, Model
import model.requests as req

class Objective:
	def __init__(self, points, description):
		self.points = points
		self.description = description

class ObjectiveVue(Objective, Vue):
	def _check(self, cursor):
		""" verifie que le nombre de point sois correct, et que la descr soit assez longue """
		return self.points.isdigit() and len(self.description) > 3

	def _send_db(self, cursor):
		cursor.add(req.new_objective(), (self.points, self.description))

class DeleteObjectiveVue(Vue):
	def __init__(self, obj_id):
		self.obj_id = obj_id

	def _check(self, cursor):
		return True

	def _send_db(self, cursor):
		cursor.add(req.delete_objective(), (self.obj_id,))

class ObjectiveModel(Objective, Model):
	def __init__(self, obj_id, points, description):
		self.obj_id = obj_id
		super().__init__(points, description)

class ObjectiveModelFromId(ObjectiveModel):
	def __init__(self, cursor, obj_id):
		super().__init__(obj_id, None, self.__load(cursor, obj_id))
		self.cursor = cursor

	def __load(self, cursor, obj_id):
		return cursor.get_one(req.objective(), (obj_id,))['description']

class ObjectivesModel(Model):
	def __init__(self, cursor):
		self.cursor = cursor
		self.objectives = self.__load_objectives()

	def __load_objectives(self):
		res = []
		req_res = self.cursor.get(req.all_objectives(), ())
		for obj in req_res:
			res.append(ObjectiveModel(obj['objective_id'], obj['points'], obj['description']))
		return res

	def to_dict(self):
		""" retourne les obj sous forme de dict """
		return {obj.obj_id: obj for obj in self.objectives}
