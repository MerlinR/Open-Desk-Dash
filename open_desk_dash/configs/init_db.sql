DROP TABLE IF EXISTS config;
DROP TABLE IF EXISTS plugins;

CREATE TABLE ODDASH (
    id INTEGER PRIMARY KEY,
    transition INTEGER NOT NULL,
    pages TEXT NOT NULL,
    auto_update INTEGER NOT NULL,
    auto_update_plugins INTEGER NOT NULL,
    theme TEXT NOT NULL,
    github TEXT NOT NULL,
    version TEXT NOT NULL,
    version_name TEXT NOT NULL,
    installed TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE plugins (
    name TEXT PRIMARY KEY,
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

INSERT INTO ODDASH (transition, pages, auto_update, auto_update_plugins, theme, github, version, version_name)
VALUES(30, "/default_dashboard/,/default_weather/,/rss_dash/", 1, 1, "default_dark", "https://github.com/MerlinR/Open-Desk-Dash", "0.1", "Alpha");