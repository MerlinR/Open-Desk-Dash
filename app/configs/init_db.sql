DROP TABLE IF EXISTS config;
DROP TABLE IF EXISTS plugins;

CREATE TABLE config (
    id INTEGER PRIMARY KEY,
    transition INTEGER NOT NULL,
    pages TEXT NOT NULL,
    version TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE plugins (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    owner TEXT NOT NULL,
    github TEXT NOT NULL,
    tag TEXT NOT NULL,
    version TEXT NOT NULL,
    pages TEXT NOT NULL,
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO config (transition,pages,version)
VALUES(30, "/default_dashboard/,/default_weather/", "0.0.1");