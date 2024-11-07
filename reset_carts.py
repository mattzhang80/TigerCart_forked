#!/usr/bin/env python
"""
reset_carts.py
Clears all user carts in the database.
"""

import sqlite3
import json

MAIN_DB_PATH = "tigercart.sqlite3"
USER_DB_PATH = "users.sqlite3"


def get_main_db_connection():
    """Returns a connection to the main database."""
    return sqlite3.connect(MAIN_DB_PATH)


def get_user_db_connection():
    """Returns a connection to the user database."""
    connection = sqlite3.connect(USER_DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def clear_and_create_empty_carts():
    """Clears all carts in the users table, setting them to empty."""
    user_conn = get_user_db_connection()
    user_cursor = user_conn.cursor()

    user_cursor.execute("UPDATE users SET cart = ?", (json.dumps({}),))

    user_conn.commit()
    user_conn.close()
    print("Carts cleared and reset to empty for all users.")


if __name__ == "__main__":
    clear_and_create_empty_carts()
