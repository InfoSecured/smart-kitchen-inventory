Smart Kitchen Inventory

A feature-rich web application to manage your home kitchen inventory. This project helps you keep track of your pantry items, manage wishlists, get recipe suggestions, and streamline shopping with barcode scanning and integrations for nutritional information and Amazon searches.

Designed to run on a Raspberry Pi or any Linux-based system, this application is accessible from your mobile device or desktop.

Features

	•	Kitchen Inventory Management: Add, update, and remove pantry items with ease.
	•	Barcode Scanning: Use your device’s camera to scan barcodes and auto-populate inventory details.
	•	Nutritional Information: Fetch nutritional details of scanned items using the Open Food Facts API.
	•	Wishlist Management: Track items you want to purchase and share wishlists with others.
	•	Recipe Suggestions: Get personalized recipe ideas based on available ingredients using Spoonacular API.
	•	Amazon Reordering: Find and reorder items from Amazon directly.
	•	Multi-User Support: Secure login with JWT-based authentication.
	•	Offline Barcode Lookup: Cache barcode data locally for offline access.

Requirements

Hardware

	•	Raspberry Pi (or any Linux-based server)
	•	Camera-enabled device for barcode scanning (e.g., smartphone)

Software

	•	Python 3.7 or higher
	•	SQLite3
	•	Nginx (for reverse proxy and HTTPS setup)

Installation

Before You Start

Make sure to replace the placeholder values in the project files:
	1.	YOUR_DOMAIN_OR_IP:
	•	Replace this with your domain name (e.g., yourdomain.com) or the public IP address of your Raspberry Pi.
	•	Found in:
	•	installation.sh (Nginx configuration section).
Example:

server_name yourdomain.com;  # Replace with your domain or public IP


	2.	your_spoonacular_api_key:
	•	Obtain an API key from Spoonacular and replace the placeholder in utils/pantry_suggestions.py.
Example:

API_KEY = “your_actual_api_key”  # Replace this with your Spoonacular API key


	3.	Optional: Amazon API:
	•	If you plan to use Amazon Product Advertising API for reordering, configure it in the relevant part of app.py (not enabled by default).
	4.	Firewall and Router Settings:
	•	If hosting publicly, open ports 80 (HTTP) and 443 (HTTPS) on your firewall and router. For local testing, ensure port 5000 is accessible.

Installation Steps

	1.	Clone the Repository

git clone https://github.com/YOUR_USERNAME/smart-kitchen-inventory.git
cd smart-kitchen-inventory


	2.	Run the Installation Script
The script installs all dependencies, initializes databases, and configures the web server.

chmod +x installation.sh
./installation.sh


	3.	Start the Application
After installation, start the Flask app:

python3 app.py


	4.	Access the App
	•	Local Network: Open your browser and go to http://<Raspberry_Pi_IP>:5000.
	•	Public Domain: Use your configured domain name (e.g., https://yourdomain.com).

Testing the App

	1.	Local Testing:
	•	Start the app: python3 app.py.
	•	Open http://<Raspberry_Pi_IP>:5000 in your browser.
	•	Test user registration, login, adding inventory, and generating wishlists.
	2.	Public Testing:
	•	Ensure your domain points to your Raspberry Pi.
	•	Open https://yourdomain.com in your browser.
	•	Test HTTPS access and Nginx configuration.

API Integrations

	1.	Open Food Facts API
	•	Used for retrieving barcode-based nutritional information.
	•	Documentation
	2.	Spoonacular API
	•	Provides recipe suggestions based on available ingredients.
	•	Documentation
	3.	Amazon Product Advertising API
	•	Enables item search and reordering on Amazon.
	•	Documentation

Troubleshooting

Common Issues

	1.	Nginx Errors
	•	Run sudo nginx -t to test your configuration and restart Nginx:

sudo systemctl restart nginx


	2.	Database Initialization Issues
	•	If the databases aren’t initialized, run:

python3 -c “from utils.db import init_db; init_db()”
python3 -c “from utils.barcode_cache import init_cache; init_cache()”


	3.	Firewall Blocking
	•	Open required ports using ufw:

sudo ufw allow 5000
sudo ufw allow 80
sudo ufw allow 443

Screenshots

Inventory Dashboard

Recipe Suggestions

Barcode Scanner

Development

Folder Structure

smart-kitchen-inventory/
├── app.py                  # Main application script
├── requirements.txt        # Python dependencies
├── installation.sh         # Installation script
├── templates/              # HTML templates
├── static/                 # Static files (CSS, JS, images)
├── utils/                  # Utility modules
├── README.md               # Documentation

Contributing

	1.	Fork the repository.
	2.	Create a new branch for your feature (git checkout -b feature-name).
	3.	Commit your changes (git commit -m “Add feature-name”).
	4.	Push to your branch (git push origin feature-name).
	5.	Create a pull request.

License

This project is licensed under the MIT License. See the LICENSE file for details.

Support

For questions or issues, feel free to open an issue in this repository.