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

Usage

Inventory Management

	•	Log in to the app.
	•	Navigate to the Inventory Dashboard.
	•	Add items manually or use the Barcode Scanner.

Wishlist

	•	Navigate to Wishlist to track items you need to purchase.
	•	Share your wishlist with friends or family using a unique URL.

Recipe Suggestions

	•	Click on Recipe Suggestions in the dashboard.
	•	View personalized recipe ideas based on your current inventory.

Barcode Scanning

	•	Use the scanner to add or remove items:
	•	Add: Scan the barcode to populate details automatically.
	•	Remove: Scan and confirm removal from the inventory.

Screenshots

Inventory Dashboard

![Inventory Dashboard](https://via.placeholder.com/