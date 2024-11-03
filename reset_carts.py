import sqlite3
import json

# Define paths to your databases
MAIN_DB_PATH = "tigercart.sqlite3"
USER_DB_PATH = "users.sqlite3"


def get_main_db_connection():
    return sqlite3.connect(MAIN_DB_PATH)


def get_user_db_connection():
    connection = sqlite3.connect(USER_DB_PATH)
    connection.row_factory = (
        sqlite3.Row
    )  # Enables dictionary-like access to rows
    return connection


def clear_and_create_empty_carts():
    # Connect to the user database
    user_conn = get_user_db_connection()
    user_cursor = user_conn.cursor()

    # Clear existing carts by setting the cart field to an empty JSON string
    user_cursor.execute("UPDATE users SET cart = ?", (json.dumps({}),))

    # Commit changes and close the connection
    user_conn.commit()
    user_conn.close()
    print("Carts cleared and reset to empty for all users.")


# Run the function
if __name__ == "__main__":
    clear_and_create_empty_carts()
