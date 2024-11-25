import sqlite3
from utils.notifications import create_notification

DB_FILE = "kitchen_inventory.db"


def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT UNIQUE,
            email_notifications BOOLEAN DEFAULT 0
        )
    ''')

    # Inventory table
    c.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            name TEXT,
            quantity INTEGER,
            unit TEXT,
            expiration_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Wishlist table
    c.execute('''
        CREATE TABLE IF NOT EXISTS wishlists (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            item_name TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Notifications table
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            message TEXT,
            is_read BOOLEAN DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()


# ----- Inventory Management -----
def add_inventory_item(user_id, name, quantity, unit, expiration_date):
    """Add a new item to the user's inventory."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO inventory (user_id, name, quantity, unit, expiration_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, name, quantity, unit, expiration_date))
    conn.commit()
    conn.close()


def get_user_inventory(user_id):
    """Retrieve all inventory items for a user."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT id, name, quantity, unit, expiration_date
        FROM inventory
        WHERE user_id = ?
    ''', (user_id,))
    inventory = c.fetchall()
    conn.close()
    return [{'id': row[0], 'name': row[1], 'quantity': row[2], 'unit': row[3], 'expiration_date': row[4]} for row in inventory]


def remove_inventory_item(item_id):
    """Remove an item from the inventory."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM inventory WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()


# ----- Wishlist Management -----
def add_wish_list_item(user_id, item_name):
    """Add a new item to the user's wishlist."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO wishlists (user_id, item_name)
        VALUES (?, ?)
    ''', (user_id, item_name))
    conn.commit()
    conn.close()


def get_user_wishlist(user_id):
    """Retrieve all wishlist items for a user."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT id, item_name
        FROM wishlists
        WHERE user_id = ?
    ''', (user_id,))
    wishlist = c.fetchall()
    conn.close()
    return [{'id': row[0], 'item_name': row[1]} for row in wishlist]


# ----- Notifications -----
def check_inventory_notifications(user_id):
    """
    Check the user's inventory for low stock or expiring items
    and create notifications as needed.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Check for low stock
    c.execute('''
        SELECT name, quantity
        FROM inventory
        WHERE user_id = ? AND quantity < 5
    ''', (user_id,))
    low_stock_items = c.fetchall()
    for item in low_stock_items:
        message = f"Low stock alert: {item[0]} has only {item[1]} remaining."
        create_notification(user_id, message)

    # Check for near-expiration items
    c.execute('''
        SELECT name, expiration_date
        FROM inventory
        WHERE user_id = ? AND expiration_date <= date('now', '+3 days')
    ''', (user_id,))
    expiring_items = c.fetchall()
    for item in expiring_items:
        message = f"Expiration alert: {item[0]} expires on {item[1]}."
        create_notification(user_id, message)

    conn.close()