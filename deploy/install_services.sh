#!/bin/bash
#
# Install systemd services and nginx configuration
# Run this on the Digital Ocean droplet as root after first deployment
#
# Usage:
#   chmod +x install_services.sh
#   sudo ./install_services.sh

set -e

APP_DIR="/var/www/todo-app"
DOMAIN="your-domain.com"  # Change this!

echo "=========================================="
echo "Installing Services and Configuration"
echo "=========================================="

# Create log directory
echo "Creating log directory..."
mkdir -p /var/log/todo-app
chown todoapp:todoapp /var/log/todo-app

# Install systemd services
echo "Installing systemd services..."
cp $APP_DIR/deploy/gunicorn.service /etc/systemd/system/
cp $APP_DIR/deploy/mcp-http.service /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Enable services
echo "Enabling services..."
systemctl enable gunicorn
systemctl enable mcp-http

# Install nginx configuration
echo "Installing nginx configuration..."
cp $APP_DIR/deploy/nginx.conf /etc/nginx/sites-available/todo-app

# Update domain in nginx config
echo "Updating domain in nginx config..."
sed -i "s/your-domain.com/$DOMAIN/g" /etc/nginx/sites-available/todo-app

# Enable nginx site
ln -sf /etc/nginx/sites-available/todo-app /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default  # Remove default site

# Test nginx configuration
echo "Testing nginx configuration..."
nginx -t

# Create environment files if they don't exist
if [ ! -f "$APP_DIR/.env.production" ]; then
    echo "Creating environment file templates..."
    cp $APP_DIR/deploy/.env.production.template $APP_DIR/.env.production
    cp $APP_DIR/deploy/.env.mcp.production.template $APP_DIR/.env.mcp.production
    chown todoapp:todoapp $APP_DIR/.env.production $APP_DIR/.env.mcp.production
    chmod 600 $APP_DIR/.env.production $APP_DIR/.env.mcp.production

    echo ""
    echo "⚠️  IMPORTANT: Edit these files and update the values:"
    echo "   - $APP_DIR/.env.production"
    echo "   - $APP_DIR/.env.mcp.production"
    echo ""
fi

# Start services
echo "Starting services..."
systemctl start gunicorn
systemctl start mcp-http
systemctl restart nginx

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Service status:"
systemctl status gunicorn --no-pager -l
systemctl status mcp-http --no-pager -l
systemctl status nginx --no-pager -l
echo ""
echo "Next steps:"
echo "1. Edit environment files:"
echo "   - $APP_DIR/.env.production"
echo "   - $APP_DIR/.env.mcp.production"
echo ""
echo "2. Generate SECRET_KEY:"
echo "   python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
echo ""
echo "3. Generate MCP tokens:"
echo "   openssl rand -hex 32"
echo ""
echo "4. Restart services:"
echo "   systemctl restart gunicorn mcp-http"
echo ""
echo "5. Set up SSL certificate:"
echo "   certbot --nginx -d $DOMAIN -d www.$DOMAIN"
echo ""
echo "6. Create superuser:"
echo "   cd $APP_DIR && source venv/bin/activate && python manage.py createsuperuser"
echo ""
