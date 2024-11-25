from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import utils.db as db
import utils.auth as auth
import utils.notifications as notifications

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config["JWT_SECRET_KEY"] = "anothersecretkey"
jwt = JWTManager(app)

# ----- Authentication -----
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
        access_token = create_access_token(identity=user['id'])
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
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('home'))


# ----- Inventory Management -----
@app.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    user_id = get_jwt_identity()
    db.check_inventory_notifications(user_id)  # Trigger notifications
    inventory = db.get_user_inventory(user_id)
    return render_template('index.html', inventory=inventory)


@app.route('/add_inventory', methods=['POST'])
@jwt_required()
def add_inventory():
    user_id = get_jwt_identity()
    data = request.json
    db.add_inventory_item(
        user_id,
        data['name'],
        data['quantity'],
        data['unit'],
        data['expiration_date']
    )
    return jsonify({'status': 'success'})


@app.route('/remove_inventory/<int:item_id>', methods=['POST'])
@jwt_required()
def remove_inventory(item_id):
    db.remove_inventory_item(item_id)
    return jsonify({'status': 'removed'})


# ----- Wishlist Management -----
@app.route('/wishlist', methods=['GET', 'POST'])
@jwt_required()
def wishlist():
    user_id = get_jwt_identity()
    if request.method == 'POST':
        data = request.form
        db.add_wish_list_item(user_id, data['item_name'])
        return redirect(url_for('wishlist'))
    wishlist_items = db.get_user_wishlist(user_id)
    return render_template('wishlist.html', wishlist_items=wishlist_items)


# ----- Notifications -----
@app.route('/notifications', methods=['GET'])
@jwt_required()
def notifications_view():
    user_id = get_jwt_identity()
    user_notifications = notifications.get_notifications(user_id)
    return render_template('notifications.html', notifications=user_notifications)


@app.route('/mark_notification_read', methods=['POST'])
@jwt_required()
def mark_notification_read():
    notification_id = request.form['notification_id']
    notifications.mark_as_read(notification_id)
    return redirect(url_for('notifications_view'))


# ----- Barcode Scanning -----
@app.route('/scan', methods=['GET'])
@jwt_required()
def scan_barcode():
    barcode = request.args.get('barcode')
    cached_data = notifications.get_cached_product(barcode)  # Check offline cache
    if cached_data:
        return jsonify(cached_data)
    
    # Fetch from Open Food Facts API
    api_url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 1:
            product = data['product']
            product_data = {
                'name': product.get('product_name', 'Unknown'),
                'nutrition': product.get('nutriments', {}),
                'image': product.get('image_url', None)
            }
            notifications.save_product(barcode, product_data)  # Save to cache
            return jsonify(product_data)
    return jsonify({'error': 'Product not found'}), 404


# ----- Recipe Suggestions -----
@app.route('/pantry_suggestions', methods=['GET'])
@jwt_required()
def pantry_suggestions():
    user_id = get_jwt_identity()
    inventory = db.get_user_inventory(user_id)
    suggestions = notifications.get_recipe_suggestions(inventory)
    return render_template('pantry.html', suggestions=suggestions)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)