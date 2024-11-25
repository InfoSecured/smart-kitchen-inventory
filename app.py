from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import utils.db as db
import utils.auth as auth
import utils.barcode_cache as cache
import utils.pantry_suggestions as pantry
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config["JWT_SECRET_KEY"] = "anothersecretkey"
jwt = JWTManager(app)

# Routes for login, register, dashboard, etc.

@app.route('/scan', methods=['GET'])
def scan_barcode():
    barcode = request.args.get('barcode')
    cached_data = cache.get_cached_product(barcode)
    if cached_data:
        return jsonify(cached_data)
    
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
            cache.save_product(barcode, product_data)
            return jsonify(product_data)
    return jsonify({'error': 'Product not found'}), 404

@app.route('/pantry_suggestions', methods=['GET'])
@jwt_required()
def pantry_suggestions():
    user = get_jwt_identity()
    inventory = db.get_user_inventory(user)
    suggestions = pantry.get_recipe_suggestions(inventory)
    return render_template('pantry.html', suggestions=suggestions)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)