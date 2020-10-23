DROP TABLE IF EXISTS card;
DROP TABLE IF EXISTS deck;

CREATE TABLE card (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    quantity INTEGER NOT NULL,
    image TEXT NOT NULL,
    back_image TEXT DEFAULT NULL,
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    price FLOAT NOT NULL,
    price_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    color TEXT
);

CREATE TABLE deck (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    colors TEXT NOT NULL,
    format TEXT NOT NULL,
    contents TEXT NOT NULL
);