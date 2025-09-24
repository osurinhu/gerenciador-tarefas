CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL
);
CREATE UNIQUE INDEX username ON users (username);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    datentime DATETIME NOT NULL,
    user_id INTEGER NOT NULL,
    active INTEGER NOT NULL, -- 0 or 1
    FOREIGN KEY(user_id) REFERENCES users(id)
);
