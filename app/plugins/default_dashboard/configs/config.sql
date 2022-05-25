DROP TABLE IF EXISTS config;

CREATE TABLE config (
    id INTEGER PRIMARY KEY,
    title INTEGER NOT NULL,
    imageLink TEXT NOT NULL
);

INSERT INTO config (title,imageLink)
VALUES("Open Desk Dash", "https://giffiles.alphacoders.com/209/209343.gif");