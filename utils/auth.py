import sqlite3
import hashlib

# Database file
DB_FILE = "kitchen_inventory.db"

def authenticate_user(username, password):
    """
    Authenticate a user by verifying their username and password.

    :param username: The username to authenticate
    :param password: The password to verify
    :return: A dictionary with user details if authentication is successful, otherwise None
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Hash the input password
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()

    # Query the database for a matching user
    c.execute("SELECT id, username, email FROM users WHERE username = ? AND password = ?", (username, hashed_pw))
    row = c.fetchone()
    conn.close()

    # Return user details as a dictionary if found
    if row:
        return {"id": row[0], "username": row[1], "email": row[2]}
    return None


def register_user(username, password, email):
    """
    Register a new user by adding them to the database.

    :param username: The username for the new user
    :param password: The password for the new user
    :param email: The email for the new user
    :return: None
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Hash the password
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()

    # Insert the new user into the database
    try:
        c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (username, hashed_pw, email))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Error: Username or email already exists.")
    finally:
        conn.close()


def check_user_exists(username):
    """
    Check if a user with the given username already exists.

    :param username: The username to check
    :return: True if the user exists, otherwise False
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Query the database for the username
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()

    return user is not None
