
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS team_users;
DROP TABLE IF EXISTS objectives;
DROP TABLE IF EXISTS pictures;
DROP TABLE IF EXISTS qrcodes;
DROP TABLE IF EXISTS team_found_qr;

PRAGMA foreign_keys = ON;

CREATE TABLE users(
	user_id INTEGER NOT NULL PRIMARY KEY,
	name TEXT NOT NULL
);

CREATE TABLE teams(
	team_id INTEGER NOT NULL PRIMARY KEY,
	color INTEGER NOT NULL,
	name TEXT NOT NULL
);

CREATE TABLE team_users(
	team_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	status INTEGER NOT NULL,
	PRIMARY KEY (user_id),
	FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
	FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE objectives(
	objective_id INTEGER NOT NULL PRIMARY KEY,
	points INTEGER NOT NULL,
	description TEXT NOT NULL
);

CREATE TABLE pictures(
	team_id INTEGER NOT NULL,
	objective_id INTEGER NOT NULL,
	filename TEXT NOT NULL,
	status INTEGER NOT NULL,
	PRIMARY KEY (team_id, objective_id),
	FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
	FOREIGN KEY (objective_id) REFERENCES objectives(objective_id) ON DELETE CASCADE
);

CREATE TABLE qrcodes(
	qr_id INTEGER NOT NULL,
	points INTEGER NOT NULL,
	PRIMARY KEY (qr_id)
);

CREATE TABLE team_found_qr(
	team_id INTEGER NOT NULL,
	qr_id INTEGER NOT NULL,
	PRIMARY KEY (team_id, qr_id),
	FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
	FOREIGN KEY (qr_id) REFERENCES qrcodes(qr_id) ON DELETE CASCADE
);
