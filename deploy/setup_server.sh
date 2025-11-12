#!/bin/bash
#
# Digital Ocean Server Setup Script
# Run this on your Digital Ocean droplet after initial creation
#
# Usage:
#   chmod +x setup_server.sh
#   sudo ./setup_server.sh

set -e  # Exit on any error

echo "=========================================="
echo "Todo App - Digital Ocean Setup"
echo "=========================================="

# Update system
echo "Updating system packages..."
apt update && apt upgrade -y

# Install required packages
echo "Installing required packages..."
apt install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    nginx \
    git \
    certbot \
    python3-certbot-nginx \
    supervisor \
    ufw

# Configure firewall
echo "Configuring firewall..."
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

# Create application user
echo "Creating application user..."
if ! id -u todoapp > /dev/null 2>&1; then
    useradd -m -s /bin/bash todoapp
    echo "User 'todoapp' created"
else
    echo "User 'todoapp' already exists"
fi

# Setup PostgreSQL
echo "Setting up PostgreSQL..."
sudo -u postgres psql <<EOF
-- Create database
CREATE DATABASE todo_production;

-- Create user
CREATE USER todoapp WITH PASSWORD 'CHANGE_THIS_PASSWORD';

-- Grant privileges
ALTER ROLE todoapp SET client_encoding TO 'utf8';
ALTER ROLE todoapp SET default_transaction_isolation TO 'read committed';
ALTER ROLE todoapp SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE todo_production TO todoapp;

-- Exit
\q
EOF

echo "PostgreSQL setup complete!"

# Create application directory
echo "Creating application directory..."
mkdir -p /var/www/todo-app
chown todoapp:todoapp /var/www/todo-app

echo ""
echo "=========================================="
echo "Server setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Run deploy.sh to deploy the application"
echo "2. Configure your domain in nginx"
echo "3. Run certbot to get SSL certificate"
echo ""
