-- schema.sql

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS cart;
DROP TABLE IF EXISTS orders;

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE cart (
    user_id INTEGER,
    item_id INTEGER,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, item_id)
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    status TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER,
    total_items INTEGER,
    cart TEXT,
    location TEXT,
    timeline TEXT,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

