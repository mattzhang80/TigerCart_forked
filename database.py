#!/usr/bin/env python
"""
database.py
Populates tigercart.sqlite3 and users.sqlite3
"""

import sqlite3

# Define database file names
MAIN_DATABASE = "tigercart.sqlite3"
USER_DATABASE = "users.sqlite3"


def get_main_db_connection():
    """Establishes and returns a connection to the main database."""
    conn = sqlite3.connect(MAIN_DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def get_user_db_connection():
    """Establishes and returns a connection to the user database."""
    conn = sqlite3.connect(USER_DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_main_db():
    """Initializes the main database with necessary tables."""
    conn = get_main_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            status TEXT CHECK(status IN ('placed', 'claimed', 'fulfilled', 'cancelled')),
            time_placed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            items TEXT,
            prices TEXT,
            quantities TEXT,
            delivery_location TEXT
        )
    """
    )

    # Removed the cart table creation from tigercart.sqlite3
    conn.commit()
    conn.close()


def init_user_db():
    """Initializes the user database with necessary tables."""
    conn = get_user_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            cart TEXT DEFAULT '{}'
        )
    """
    )

    conn.commit()
    conn.close()


def populate_items(sample_items):
    """Populates the items table with sample data."""
    conn = get_main_db_connection()
    cursor = conn.cursor()

    for item_id, item in sample_items.items():
        cursor.execute(
            "INSERT OR IGNORE INTO items (id, name, price, category) VALUES (?, ?, ?, ?)",
            (item_id, item["name"], item["price"], item["category"]),
        )

    conn.commit()
    conn.close()


def populate_sample_items():
    """Populates the items table with predefined sample data."""
    sample_items = {
        "1": {"name": "Coke", "price": 1.09, "category": "drinks"},
        "2": {"name": "Diet Coke", "price": 1.29, "category": "drinks"},
        "3": {
            "name": "Tropicana Orange Juice",
            "price": 0.89,
            "category": "drinks",
        },
        "4": {
            "name": "Lay’s Potato Chips",
            "price": 1.59,
            "category": "food",
        },
        "5": {
            "name": "Snickers Bar",
            "price": 0.99,
            "category": "food",
        },
        "6": {"name": "Notebook", "price": 2.49, "category": "other"},
    }
    populate_items(sample_items)
    print("Sample items populated.")


def populate_users():
    """Populates the users table with initial users."""
    conn = get_user_db_connection()
    cursor = conn.cursor()

    # Add initial users
    users = [
        (1, "Connor"),
        (2, "Jacob"),
        (3, "Alex"),
        (4, "Matt"),
        (5, "Okezie"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO users (user_id, name) VALUES (?, ?)",
        users,
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_main_db()  # Create the tables if they don't exist
    init_user_db()  # Create the user table if it doesn't exist
    populate_sample_items()  # Populate items table with sample data
    populate_users()  # Populate users table with initial users
