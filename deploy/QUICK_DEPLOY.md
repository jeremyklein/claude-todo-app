# Quick Deploy Reference

## One-Time Setup (First Deployment)

### On Your Local Machine

```bash
# Make scripts executable
chmod +x deploy/*.sh
```

### On Digital Ocean Droplet

```bash
# 1. SSH into droplet
ssh root@your-droplet-ip

# 2. Upload and run server setup
scp deploy/setup_server.sh root@your-droplet-ip:/root/
ssh root@your-droplet-ip
chmod +x setup_server.sh
./setup_server.sh

# 3. Deploy application (from local machine)
cd /Users/jeremyklein/development/todo-app
./deploy/deploy.sh your-droplet-ip

# 4. Install services (on droplet)
ssh root@your-droplet-ip
cd /var/www/todo-app/deploy
chmod +x install_services.sh
nano install_services.sh  # Set your domain
./install_services.sh

# 5. Configure environment (on droplet)
cd /var/www/todo-app
nano .env.production        # Update SECRET_KEY, DB_PASSWORD, ALLOWED_HOSTS
nano .env.mcp.production    # Update MCP_AUTH_TOKEN, DB_PASSWORD

# Generate values:
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
openssl rand -hex 32

# 6. Restart services
systemctl restart gunicorn mcp-http nginx

# 7. Create superuser
cd /var/www/todo-app
source venv/bin/activate
python manage.py createsuperuser

# 8. Get SSL certificate
certbot --nginx -d your-domain.com -d www.your-domain.com
```

## Subsequent Deployments

```bash
# From your local machine
cd /Users/jeremyklein/development/todo-app
./deploy/deploy.sh your-domain.com
```

That's it! The script handles everything.

## Common Commands

```bash
# Restart services
systemctl restart gunicorn mcp-http nginx

# View logs
journalctl -u gunicorn -f
journalctl -u mcp-http -f

# Django management
cd /var/www/todo-app && source venv/bin/activate
python manage.py <command>

# Check status
systemctl status gunicorn mcp-http nginx
```

## URLs After Deployment

- **Web App**: https://your-domain.com
- **Admin**: https://your-domain.com/admin
- **API Docs**: https://your-domain.com/api/v1/docs/
- **MCP Server**: https://your-domain.com/mcp/

## File Checklist

Before first deployment, verify these files exist:

- [ ] `deploy/setup_server.sh` - Initial server setup
- [ ] `deploy/deploy.sh` - Deployment script
- [ ] `deploy/install_services.sh` - Service installation
- [ ] `deploy/gunicorn.service` - Django service config
- [ ] `deploy/mcp-http.service` - MCP service config
- [ ] `deploy/nginx.conf` - Nginx configuration
- [ ] `deploy/.env.production.template` - Django env template
- [ ] `deploy/.env.mcp.production.template` - MCP env template

All files are created and ready to use!
