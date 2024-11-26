from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import utils.db as db
import utils.auth as auth
import requests
from utils.db import get_db_connection

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Ensure this is secure and unique in production

# ----- Debugging: List All Routes -----
from flask import url_for

@app.before_first_request
def list_routes():
    print("\n=== Registered Routes ===")
    for rule in app.url_map.iter_rules():
        print(f"Route: {rule}, Endpoint: {rule.endpoint}")
    print("=========================\n")

# ----- Middleware to Enforce Authentication -----
protected_routes = ['dashboard', 'wishlist', 'notifications_view', 'pantry_suggestions', 'add_item']

@app.before_request
def check_authentication():
    if request.endpoint in protected_routes:
        if 'user_id' not in session:
            return jsonify({"msg": "Authorization required"}), 401

# ----- Home and Authentication -----
@app.route('/', methods=['GET'])
def home():
    if "username" in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.form
    user = auth.authenticate_user(data['username'], data['password'])
    if user:
        session['username'] = user['username']
        session['user_id'] = user['id']
        return redirect(url_for('dashboard'))
    return "Invalid username or password", 401

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        auth.register_user(data['username'], data['password'], data['email'])
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('home'))

# ----- Inventory Management -----
@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    inventory = conn.execute("SELECT * FROM inventory").fetchall()
    conn.close()
    return render_template('dashboard.html', inventory=inventory)

@app.route('/add_inventory', methods=['POST'])
def add_inventory():
    name = request.form.get('name')
    quantity = request.form.get('quantity')
    unit = request.form.get('unit')
    expiration_date = request.form.get('expiration_date')

    # Debugging logs
    print(f"Form Data - Name: {name}, Quantity: {quantity}, Unit: {unit}, Expiration Date: {expiration_date}")

    if not name or not quantity or int(quantity) <= 0:
        print("Invalid input detected.")
        return "Invalid item name or quantity", 400

    conn = get_db_connection()
    existing_item = conn.execute(
        "SELECT * FROM inventory WHERE name = ? AND unit = ?", (name, unit)
    ).fetchone()

    if existing_item:
        # Update the quantity of the existing item
        new_quantity = existing_item['quantity'] + int(quantity)
        conn.execute(
            "UPDATE inventory SET quantity = ? WHERE id = ?", (new_quantity, existing_item['id'])
        )
        print(f"Updated Item - ID: {existing_item['id']}, New Quantity: {new_quantity}")
    else:
        # Insert a new item if it doesn't exist
        conn.execute(
            "INSERT INTO inventory (name, quantity, unit, expiration_date) VALUES (?, ?, ?, ?)",
            (name, int(quantity), unit, expiration_date),
        )
        print(f"Inserted New Item - Name: {name}, Quantity: {quantity}, Unit: {unit}, Expiration Date: {expiration_date}")

    conn.commit()
    conn.close()

    return redirect('/dashboard')

@app.route('/update_inventory/<int:item_id>', methods=['POST'])
def update_inventory(item_id):
    print(f"Update inventory called for item_id={item_id}")

    inventory_item = db.get_inventory_item_by_id(item_id)  # No user_id filtering
    if inventory_item:
        action = request.form.get('action')  # "decrease" or "remove_all"
        print(f"Action received: {action}")

        if action == "decrease":
            new_quantity = inventory_item['quantity'] - 1
            if new_quantity > 0:
                db.update_inventory_quantity(item_id, new_quantity)
                print(f"Reduced quantity for item_id={item_id} to {new_quantity}")
            else:
                db.remove_inventory_item(item_id)
                print(f"Deleted item_id={item_id} as quantity reached 0")

        elif action == "remove_all":
            db.remove_inventory_item(item_id)
            print(f"Deleted all of item_id={item_id}")
    else:
        print(f"Item with item_id={item_id} not found.")

    return redirect(url_for('dashboard'))

# ----- Add Item and Barcode Scanning -----
@app.route('/add_item', methods=['GET'])
def add_item():
    barcode = request.args.get('barcode')
    name = request.args.get('name')

    # If name is missing, assume manual entry
    if not name:
        return render_template('add_item.html', barcode=barcode)

    # Render the form with prefilled product name
    return render_template('add_item.html', barcode=barcode, name=name)

@app.route('/scan_barcode', methods=['GET'])
def scan_barcode():
    return render_template('scan_barcode.html')

# ----- Notifications -----
@app.route('/notifications', methods=['GET'])
def notifications_view():
    user_id = session['user_id']
    user_notifications = db.get_notifications(user_id)
    return render_template('notifications.html', notifications=user_notifications)

@app.route('/mark_notification_read', methods=['POST'])
def mark_notification_read():
    notification_id = request.form['notification_id']
    db.mark_as_read(notification_id)
    return redirect(url_for('notifications_view'))

# ----- Recipe Suggestions -----
@app.route('/pantry_suggestions', methods=['GET'])
def pantry_suggestions():
    user_id = session['user_id']
    inventory = db.get_user_inventory(user_id)
    suggestions = db.get_recipe_suggestions(inventory)
    return render_template('pantry.html', suggestions=suggestions)

# ----- Debug: Barcode Lookup -----
@app.route('/lookup_barcode', methods=['GET'])
def lookup_barcode():
    barcode = request.args.get('barcode')
    if not barcode:
        return jsonify({"error": "Missing barcode parameter"}), 400

    # Validate barcode length
    if len(barcode) not in [12, 13]:
        return jsonify({"error": f"Invalid barcode length ({len(barcode)})."}), 400

    # Remove leading zeros
    cleaned_barcode = barcode.lstrip("0")

    # Query UPCitemDB Free API
    response = requests.get(f"https://api.upcitemdb.com/prod/trial/lookup", params={"upc": cleaned_barcode})
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch product information"}), 500

    data = response.json()
    if "items" in data and len(data["items"]) > 0:
        product = data["items"][0]
        return jsonify({
            "name": product["title"],
            "brand": product.get("brand", "Unknown Brand"),
            "description": product.get("description", "No description available.")
        })

    return jsonify({
        "error": f"Product not found for barcode {cleaned_barcode}. It may not be available in the UPCitemDB database."
    }), 404

# ----- Wishlist -----
@app.route('/wishlist', methods=['GET', 'POST'])
def wishlist():
    """Handle wishlist operations."""
    user_id = session['user_id']
    if request.method == 'POST':
        data = request.form
        db.add_wish_list_item(user_id, data['item_name'])
        return redirect(url_for('wishlist'))
    wishlist_items = db.get_user_wishlist(user_id)
    return render_template('wishlist.html', wishlist_items=wishlist_items)


# ----- Run Flask App -----
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
