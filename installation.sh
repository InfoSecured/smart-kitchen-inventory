#!/bin/bash

echo "Starting installation of Smart Kitchen Inventory..."

# Step 1: Update System
echo "Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Step 2: Install Dependencies
echo "Installing required software..."
sudo apt install python3 python3-pip sqlite3 nginx certbot python3-certbot-nginx -y

# Step 3: Install Python Packages
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Step 4: Initialize Databases
echo "Initializing databases..."
python3 -c "from utils.db import init_db; init_db()"
python3 -c "from utils.barcode_cache import init_cache; init_cache()"

# Step 5: Configure Nginx
echo "Configuring Nginx for reverse proxy..."
NGINX_CONF="/etc/nginx/sites-available/smart-kitchen"
sudo cat <<EOF > $NGINX_CONF
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF
sudo ln -s $NGINX_CONF /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# Step 6: Enable HTTPS
echo "Setting up HTTPS with Certbot..."
sudo certbot --nginx -d YOUR_DOMAIN_OR_IP

# Step 7: Run the Application
echo "Installation complete! Run the app with: python3 app.py"