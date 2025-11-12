# Digital Ocean Deployment Guide

Complete guide to deploy your Django Todo App with MCP HTTP server to Digital Ocean.

## Prerequisites

- Digital Ocean account
- Domain name (optional but recommended)
- SSH key configured
- Local Git repository

## Quick Start

### 1. Create Digital Ocean Droplet

1. Log in to Digital Ocean
2. Create new droplet:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic ($6/month minimum recommended)
   - **CPU**: Regular Intel (Shared CPU)
   - **Datacenter**: Choose closest to you
   - **Authentication**: SSH key (recommended)
   - **Hostname**: todo-app

3. Wait for droplet to be created and note the IP address

### 2. Point Domain to Droplet (Optional)

If you have a domain:
1. Go to your domain registrar
2. Add A record: `@` → Your droplet IP
3. Add A record: `www` → Your droplet IP
4. Wait for DNS propagation (5-30 minutes)

### 3. Initial Server Setup

SSH into your droplet:
```bash
ssh root@your-droplet-ip
```

Run the server setup script:
```bash
# Upload setup script
scp deploy/setup_server.sh root@your-droplet-ip:/root/

# SSH into server
ssh root@your-droplet-ip

# Run setup
chmod +x setup_server.sh
./setup_server.sh
```

This will:
- Update system packages
- Install Python 3.12, PostgreSQL, Nginx
- Create `todoapp` user
- Set up PostgreSQL database
- Configure firewall

### 4. Deploy the Application

From your local machine:

```bash
cd /Users/jeremyklein/development/todo-app
chmod +x deploy/deploy.sh
./deploy.sh your-droplet-ip
```

### 5. Configure Services

SSH back into your droplet:
```bash
ssh root@your-droplet-ip
cd /var/www/todo-app/deploy
chmod +x install_services.sh

# Edit this file first and set your domain!
nano install_services.sh  # Change DOMAIN variable

./install_services.sh
```

### 6. Configure Environment Variables

**Django environment** (`/var/www/todo-app/.env.production`):
```bash
cd /var/www/todo-app
nano .env.production
```

Update these values:
```bash
# Generate secret key
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Update in .env.production:
SECRET_KEY=<generated-key>
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-droplet-ip
DB_PASSWORD=<your-postgres-password>
```

**MCP environment** (`/var/www/todo-app/.env.mcp.production`):
```bash
nano .env.mcp.production
```

Update these values:
```bash
# Generate tokens
openssl rand -hex 32  # For MCP_AUTH_TOKEN
openssl rand -hex 32  # For user tokens (if needed)

# Update in .env.mcp.production:
MCP_AUTH_TOKEN=<generated-token>
DB_PASSWORD=<same-as-django>
```

**Restart services** after editing:
```bash
systemctl restart gunicorn mcp-http nginx
```

### 7. Create Superuser

```bash
cd /var/www/todo-app
source venv/bin/activate
python manage.py createsuperuser
```

### 8. Set Up SSL Certificate (Recommended)

If you have a domain:
```bash
certbot --nginx -d your-domain.com -d www.your-domain.com
```

Follow the prompts. This will:
- Obtain free SSL certificate from Let's Encrypt
- Automatically configure nginx for HTTPS
- Set up auto-renewal

## Verify Deployment

### Check Services

```bash
# Check all services are running
systemctl status gunicorn
systemctl status mcp-http
systemctl status nginx

# Check logs
journalctl -u gunicorn -f
journalctl -u mcp-http -f
tail -f /var/log/nginx/todo-app-access.log
```

### Test the Application

1. **Web UI**: http://your-domain.com or http://your-droplet-ip
2. **Admin**: http://your-domain.com/admin
3. **API**: http://your-domain.com/api/v1/
4. **MCP HTTP**: http://your-domain.com/mcp/health

### Test MCP Server

```bash
# From your local machine or server
curl https://your-domain.com/mcp/health

curl -X POST https://your-domain.com/mcp/messages \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {}
  }'
```

## Directory Structure on Server

```
/var/www/todo-app/
├── venv/                    # Django virtual environment
├── venv-mcp/                # MCP virtual environment
├── todo_project/            # Django project
├── tasks/                   # Django app
├── static/                  # Static files (source)
├── staticfiles/             # Collected static files
├── media/                   # User uploads
├── deploy/                  # Deployment scripts
├── .env.production          # Django environment
├── .env.mcp.production      # MCP environment
├── manage.py
├── mcp_server_http.py
└── gunicorn.sock           # Gunicorn socket

/etc/systemd/system/
├── gunicorn.service         # Django service
└── mcp-http.service         # MCP service

/etc/nginx/sites-available/
└── todo-app                 # Nginx config

/var/log/todo-app/
├── gunicorn-access.log
├── gunicorn-error.log
├── mcp-http.log
└── mcp-http-error.log
```

## Common Commands

### Restart Services

```bash
# Restart Django
systemctl restart gunicorn

# Restart MCP
systemctl restart mcp-http

# Restart Nginx
systemctl restart nginx

# Restart all
systemctl restart gunicorn mcp-http nginx
```

### View Logs

```bash
# Django logs
journalctl -u gunicorn -f

# MCP logs
journalctl -u mcp-http -f
tail -f /var/log/todo-app/mcp-http.log

# Nginx logs
tail -f /var/log/nginx/todo-app-access.log
tail -f /var/log/nginx/todo-app-error.log
```

### Update Application

From your local machine:
```bash
cd /Users/jeremyklein/development/todo-app
./deploy/deploy.sh your-domain.com
```

This will:
- Create deployment package
- Upload to server
- Extract files
- Install dependencies
- Run migrations
- Collect static files
- Restart services

### Django Management Commands

```bash
cd /var/www/todo-app
source venv/bin/activate

# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Django shell
python manage.py shell

# Create sample data
python create_sample_data.py
```

## Security Checklist

### Initial Setup
- [ ] Changed PostgreSQL password
- [ ] Generated new SECRET_KEY
- [ ] Generated new MCP_AUTH_TOKEN
- [ ] Set DEBUG=False
- [ ] Configured ALLOWED_HOSTS
- [ ] Set up firewall (UFW)
- [ ] Configured SSH key authentication
- [ ] Disabled root password login

### SSL/HTTPS
- [ ] Obtained SSL certificate
- [ ] Enabled HTTPS redirect
- [ ] Set SECURE_SSL_REDIRECT=True
- [ ] Set SESSION_COOKIE_SECURE=True
- [ ] Set CSRF_COOKIE_SECURE=True

### Ongoing
- [ ] Regular backups (database + media)
- [ ] Monitor logs for errors
- [ ] Keep system updated: `apt update && apt upgrade`
- [ ] Rotate MCP tokens periodically
- [ ] Monitor disk space

## Backup and Restore

### Backup Database

```bash
# On server
sudo -u postgres pg_dump todo_production > backup_$(date +%Y%m%d).sql

# Download to local
scp root@your-droplet-ip:/path/to/backup_*.sql ~/backups/
```

### Restore Database

```bash
# On server
sudo -u postgres psql todo_production < backup_20250112.sql
```

### Backup Media Files

```bash
# On server
tar -czf media_backup_$(date +%Y%m%d).tar.gz /var/www/todo-app/media

# Download to local
scp root@your-droplet-ip:/path/to/media_backup_*.tar.gz ~/backups/
```

## Troubleshooting

### Services Won't Start

```bash
# Check status
systemctl status gunicorn
systemctl status mcp-http

# Check logs
journalctl -u gunicorn -n 50
journalctl -u mcp-http -n 50

# Common issues:
# - Environment file missing or incorrect
# - Database connection failed
# - Permission issues
```

### Fix Permissions

```bash
chown -R todoapp:todoapp /var/www/todo-app
chmod 600 /var/www/todo-app/.env*
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
sudo -u postgres psql todo_production

# Check if database exists
sudo -u postgres psql -l

# Verify user permissions
sudo -u postgres psql -c "\du"
```

### Nginx 502 Bad Gateway

```bash
# Check if gunicorn is running
systemctl status gunicorn

# Check socket file exists
ls -l /var/www/todo-app/gunicorn.sock

# Check nginx error log
tail -f /var/log/nginx/todo-app-error.log
```

### Static Files Not Loading

```bash
cd /var/www/todo-app
source venv/bin/activate
python manage.py collectstatic --noinput

# Check permissions
ls -la staticfiles/
```

## Monitoring

### Set Up Monitoring (Optional)

Install monitoring tools:
```bash
apt install htop nethogs iotop
```

Monitor resources:
```bash
# CPU and memory
htop

# Network usage
nethogs

# Disk I/O
iotop

# Disk space
df -h
```

### Log Rotation

Logs are automatically rotated by systemd. To check:
```bash
journalctl --disk-usage
```

## Scaling

### Increase Gunicorn Workers

Edit `/etc/systemd/system/gunicorn.service`:
```
--workers 5  # 2-4 workers per CPU core
```

Restart:
```bash
systemctl daemon-reload
systemctl restart gunicorn
```

### Add More RAM

If running out of memory:
1. Resize droplet in Digital Ocean dashboard
2. Restart server
3. Increase workers if needed

## Cost Estimate

### Monthly Costs

- **Basic Droplet** ($6/month): 1GB RAM, 1 CPU - Good for testing
- **Standard Droplet** ($12/month): 2GB RAM, 1 CPU - Recommended for production
- **Performance Droplet** ($24/month): 4GB RAM, 2 CPU - For heavy use

### Additional Costs

- Domain name: $10-15/year
- Backups: $1.20/month (20% of droplet cost)
- Bandwidth: Included (1TB)

## Next Steps After Deployment

1. **Set up automated backups**
   - Use Digital Ocean backup feature
   - Or set up cron job for database dumps

2. **Configure monitoring**
   - Set up UptimeRobot for uptime monitoring
   - Configure email alerts

3. **Create additional users**
   - Add team members via Django admin
   - Generate MCP tokens for each user

4. **Customize**
   - Update branding and styling
   - Add custom domain email
   - Configure email notifications

## Support

If you encounter issues:

1. Check logs: `journalctl -u gunicorn -f`
2. Verify environment files
3. Test database connection
4. Check nginx configuration: `nginx -t`
5. Restart services: `systemctl restart gunicorn mcp-http nginx`

## Summary

✅ Your Django Todo App is now deployed to Digital Ocean!

- **Web UI**: https://your-domain.com
- **Admin**: https://your-domain.com/admin
- **API**: https://your-domain.com/api/v1/
- **MCP Server**: https://your-domain.com/mcp/

Both the Django web app and MCP HTTP server are running as systemd services with automatic restart on failure.

Enjoy your production todo app! 🎉
