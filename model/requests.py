
def user_with_name():
	return """ SELECT user_id FROM users WHERE name = ? """

def new_user():
	return """ INSERT INTO users(name) VALUES (?) """

def delete_user():
	return """ DELETE FROM users WHERE user_id = ? """

def user():
	return """ SELECT * FROM users WHERE user_id = ? """

def users():
	return """ SELECT * FROM users """

def all_teams():
	return """ SELECT * FROM teams """

def team():
	return """ SELECT * FROM teams WHERE team_id = ? """

def team_with_name():
	return """ SELECT team_id FROM teams WHERE name = ? """

def team_id_of_user():
	return """ SELECT team_id, status FROM team_users WHERE user_id = ? """

def team_of_user():
	return """ SELECT team_id FROM team_users WHERE user_id = ?  """

def users_of_team():
	return """ SELECT u.user_id, u.name FROM users as u, teams as t, team_users as tu WHERE t.team_id = ? AND tu.team_id = t.team_id AND tu.user_id = u.user_id """

def new_team():
	return """ INSERT INTO teams(name, color) VALUES (?, ?) """

def delete_team():
	return """ DELETE FROM teams WHERE team_id = ? """

def add_teammate():
	return """ INSERT INTO team_users(team_id, user_id, status) VALUES (?, ?, ?) """

def leave_team():
	return """ DELETE FROM team_users WHERE user_id = ? """

def new_objective():
	return """ INSERT INTO objectives(points, description) VALUES (?, ?) """

def objective():
	return """ SELECT * FROM objectives WHERE objective_id = ? """

def all_objectives():
	return """ SELECT * FROM objectives """

def delete_objective():
	return """ DELETE FROM objectives WHERE objective_id = ? """

def picture_of_team():
	return """ SELECT * FROM pictures WHERE team_id = ? AND objective_id = ? """

def add_picture():
	return """ INSERT INTO pictures(team_id, objective_id, filename, status) VALUES (?, ?, ?, ?) """

def delete_picture():
	return """ DELETE FROM pictures WHERE team_id = ? AND objective_id = ? """

def accept_picture():
	return """ UPDATE pictures SET status = 1 WHERE team_id = ? AND objective_id = ? """

def get_picture():
	return """ SELECT * FROM pictures WHERE team_id = ? AND objective_id = ? """

def get_team_pictures():
	return """ SELECT * FROM pictures WHERE team_id = ? """

def get_all_pictures():
	return """ SELECT * FROM pictures """

def get_pictures_w_status():
	return """ SELECT * FROM pictures WHERE status = ? """

def get_team_points_from_objs():
	return """ 
		SELECT
			t.team_id,
			SUM(o.points) as points
		FROM
			objectives as o,
			teams as t,
			pictures as p
		WHERE
			p.team_id = t.team_id
			AND p.objective_id = o.objective_id
			AND t.team_id = ?
		GROUP BY
			t.team_id
		"""

def get_team_points_from_qrs():
	return """ 
		SELECT
			t.team_id,
			SUM(qr.points) as points
		FROM
			qrcodes as qr,
			teams as t,
			team_found_qr as has_qr
		WHERE
			has_qr.team_id = t.team_id
			AND has_qr.qr_id = qr.qr_id
			AND t.team_id = ?
		GROUP BY
			t.team_id
		"""

def get_points_from_objs():
	return """
		SELECT
			t.team_id as team_id,
			SUM(o.points) as points
		FROM
			objectives as o,
			teams as t,
			pictures as p
		WHERE
			p.team_id = t.team_id
			AND p.objective_id = o.objective_id
		GROUP BY
			t.team_id
	"""

def get_points_from_qrs():
	return """
		SELECT
			t.team_id as team_id,
			SUM(qr.points) as points
		FROM
			qrcodes as qr,
			teams as t,
			team_found_qr as has_qr
		WHERE
			has_qr.team_id = t.team_id
			AND has_qr.qr_id = qr.qr_id
		GROUP BY
			t.team_id
	"""

def new_qr():
	return """ INSERT INTO qrcodes(key, points, description) VALUES (?, ?, ?) """

def delete_qr():
	return """ DELETE FROM qrcodes WHERE key = ? """

def all_qrcodes():
	return """ SELECT * FROM qrcodes """

def qr_from_key():
	return """ SELECT * FROM qrcodes WHERE key = ? """

def has_found_qr():
	return """ SELECT * FROM team_found_qr WHERE team_id = ? AND qr_id = ? """

def found_qr():
	return """ INSERT INTO team_found_qr(team_id, qr_id) VALUES (?, ?) """
