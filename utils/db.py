import sqlite3
import requests

# Database file location
DB_FILE = "kitchen_inventory.db"

# Spoonacular API configuration
SPOONACULAR_API_KEY = "INSERT API KEY HERE"  # Replace with your Spoonacular API key
SPOONACULAR_API_URL = "https://api.spoonacular.com/recipes/findByIngredients"

# ----- Database Initialization -----
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
            expiration_date DATE NULL,
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

def get_db_connection():
    """
    Create and return a connection to the SQLite database.
    """
    conn = sqlite3.connect('inventory.db')  # Ensure the database file name is correct
    conn.row_factory = sqlite3.Row  # Access rows as dictionaries
    return conn

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

def get_all_inventory():
    """Retrieve all inventory items."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT id, name, quantity, unit, expiration_date
        FROM inventory
    ''')
    inventory = c.fetchall()
    conn.close()
    return [{'id': row[0], 'name': row[1], 'quantity': row[2], 'unit': row[3], 'expiration_date': row[4]} for row in inventory]

def get_inventory_item_by_id(item_id):
    conn = get_db_connection()
    query = "SELECT * FROM inventory WHERE id = ?"
    print(f"Executing query: {query} with item_id={item_id}")
    item = conn.execute(query, (item_id,)).fetchone()
    conn.close()
    print(f"Query result: {item}")
    return item

def update_inventory_quantity(item_id, new_quantity):
    conn = get_db_connection()
    conn.execute("UPDATE inventory SET quantity = ? WHERE id = ?", (new_quantity, item_id))
    conn.commit()
    conn.close()

def remove_inventory_item(item_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
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

def create_notification(user_id, message):
    """Create a new notification for a user."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO notifications (user_id, message, is_read)
            VALUES (?, ?, 0)
        ''', (user_id, message))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating notification: {e}")
    finally:
        conn.close()

def get_notifications(user_id):
    """Retrieve all notifications for a user."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT id, message, is_read, created_at
        FROM notifications
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (user_id,))
    notifications = c.fetchall()
    conn.close()

    # Convert the result into a list of dictionaries
    return [
        {
            'id': row[0],
            'message': row[1],
            'is_read': bool(row[2]),
            'created_at': row[3]
        }
        for row in notifications
    ]

def mark_as_read(notification_id):
    """Mark a notification as read."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        UPDATE notifications
        SET is_read = 1
        WHERE id = ?
    ''', (notification_id,))
    conn.commit()
    conn.close()

# ----- Recipe Suggestions -----
def get_recipe_suggestions(inventory):
    """
    Fetch recipe suggestions from Spoonacular API based on inventory.

    :param inventory: A list of inventory items (dictionaries)
    :return: A list of recipe suggestions
    """
    ingredients = [item['name'] for item in inventory]

    params = {
        'ingredients': ','.join(ingredients),
        'number': 5,  # Number of recipes to fetch
        'apiKey': SPOONACULAR_API_KEY
    }

    try:
        response = requests.get(SPOONACULAR_API_URL, params=params)
        response.raise_for_status()
        recipes = response.json()
        return recipes

    except requests.RequestException as e:
        print(f"Error fetching recipes: {e}")
        return []
