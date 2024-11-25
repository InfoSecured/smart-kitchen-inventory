import sqlite3

DB_FILE = "kitchen_inventory.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT UNIQUE
    )''')
    # Inventory table
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        name TEXT,
        quantity INTEGER,
        expiration_date TEXT
    )''')
    # Wish list table
    c.execute('''CREATE TABLE IF NOT EXISTS wishlists (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        item_name TEXT
    )''')
    conn.commit()
    conn.close()