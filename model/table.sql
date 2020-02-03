
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS team_users;
DROP TABLE IF EXISTS objectives;
DROP TABLE IF EXISTS pictures;

PRAGMA foreign_keys = ON;

CREATE TABLE users(
	user_id INTEGER NOT NULL PRIMARY KEY,
	name TEXT NOT NULL,
);

CREATE TABLE teams(
	team_id INTEGER NOT NULL PRIMARY KEY,
	name TEXT NOT NULL
);

CREATE TABLE team_users(
	team_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	PRIMARY KEY (team_id, user_id),
	FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
	FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
);

CREATE TABLE objectives(
	objective_id INTEGER NOT NULL PRIMARY KEY,
	points INTEGER NOT NULL,
	description TEXT NOT NULL
);

CREATE TABLE pictures(
	picture_id INTEGER NOT NULL PRIMARY KEY,
	objective_id INTEGER NOT NULL,
	url TEXT NOT NULL,
	FOREIGN KEY (objective_id) REFERENCES objectives(objective_id) ON DELETE CASCADE
);
