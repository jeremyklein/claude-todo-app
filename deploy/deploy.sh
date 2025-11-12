#!/bin/bash
#
# Deploy Todo App to Digital Ocean
# Run this from your local machine
#
# Usage:
#   ./deploy.sh <droplet-ip-or-domain>
#
# Example:
#   ./deploy.sh 123.456.789.0
#   ./deploy.sh todo.example.com

set -e

if [ -z "$1" ]; then
    echo "Usage: ./deploy.sh <droplet-ip-or-domain>"
    exit 1
fi

SERVER=$1
APP_DIR="/var/www/todo-app"

echo "=========================================="
echo "Deploying to: $SERVER"
echo "=========================================="

# Create deployment archive
echo "Creating deployment package..."
cd ..
tar -czf /tmp/todo-app-deploy.tar.gz \
    --exclude='venv' \
    --exclude='venv-mcp' \
    --exclude='db.sqlite3' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='deploy/deploy.sh' \
    .

# Copy to server
echo "Copying files to server..."
scp /tmp/todo-app-deploy.tar.gz root@$SERVER:/tmp/

# Deploy on server
echo "Deploying on server..."
ssh root@$SERVER << 'ENDSSH'
set -e

APP_DIR="/var/www/todo-app"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup existing deployment
if [ -d "$APP_DIR" ]; then
    echo "Backing up existing deployment..."
    cp -r $APP_DIR ${APP_DIR}_backup_$TIMESTAMP
fi

# Create app directory
mkdir -p $APP_DIR
cd $APP_DIR

# Extract new code
echo "Extracting files..."
tar -xzf /tmp/todo-app-deploy.tar.gz -C $APP_DIR
rm /tmp/todo-app-deploy.tar.gz

# Set ownership
chown -R todoapp:todoapp $APP_DIR

# Switch to app user
sudo -u todoapp bash << 'ENDUSER'
set -e
cd /var/www/todo-app

# Create virtual environments
echo "Creating virtual environments..."
python3.12 -m venv venv
python3.12 -m venv venv-mcp

# Install dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
deactivate

source venv-mcp/bin/activate
pip install --upgrade pip
pip install -r requirements-mcp.txt
deactivate

# Run migrations
echo "Running database migrations..."
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput

# Create superuser if needed (you'll need to do this manually first time)
# python manage.py createsuperuser

deactivate

echo "Deployment complete for app user"
ENDUSER

# Restart services
echo "Restarting services..."
systemctl restart gunicorn
systemctl restart mcp-http
systemctl restart nginx

echo "Deployment complete!"
echo "Check status with: systemctl status gunicorn mcp-http nginx"

ENDSSH

echo ""
echo "=========================================="
echo "Deployment successful!"
echo "=========================================="
echo ""
echo "Your app should now be running at: http://$SERVER"
echo ""
echo "Next steps:"
echo "1. Set up SSL: sudo certbot --nginx -d your-domain.com"
echo "2. Create admin user: cd $APP_DIR && source venv/bin/activate && python manage.py createsuperuser"
echo "3. Configure environment variables in /var/www/todo-app/.env"
echo ""
