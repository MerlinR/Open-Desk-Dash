DROP TABLE IF EXISTS config;
DROP TABLE IF EXISTS plugins;

CREATE TABLE config (
    id INTEGER PRIMARY KEY,
    transition INTEGER NOT NULL,
    pages TEXT NOT NULL,
    autoUpdate INTEGER NOT NULL,
    autoUpdatePlugins INTEGER NOT NULL,
    theme TEXT NOT NULL,
    github TEXT NOT NULL,
    version TEXT NOT NULL,
    versionName TEXT NOT NULL,
    installed TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE plugins (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    author TEXT NOT NULL,
    github TEXT NOT NULL,
    path TEXT NOT NULL,
    version TEXT NOT NULL,
    tag TEXT,
    tagName TEXT,
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO config (transition, pages, autoUpdate, autoUpdatePlugins, theme, github, version, versionName)
VALUES(30, "/default_dashboard/,/default_weather/", 1, 1, "default", "https://github.com/MerlinR/Open-Desk-Dash", "0.1", "Alpha");