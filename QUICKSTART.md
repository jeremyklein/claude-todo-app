# Quick Start Guide

## Start the Application

1. Activate virtual environment:
```bash
source venv/bin/activate
```

2. Start the server:
```bash
python manage.py runserver
```

3. Open your browser:
- **App**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/

## Login Credentials

- **Username**: admin
- **Password**: admin123

## What's Included

The app comes pre-loaded with:
- 5 Categories (Work, Personal, Health, Learning, Home)
- 10 Sample Tasks (various statuses and priorities)
- Fully configured admin interface
- Complete styling

## Key Features to Try

1. **Dashboard** - See your effort points for today/week/month/year
2. **Create Task** - Add a new task with priority and effort points
3. **Complete Task** - Mark a task complete and see points update
4. **Analytics** - View your productivity charts and stats
5. **Admin** - Bulk actions and advanced management

## Common Commands

```bash
# Create new user
python manage.py createsuperuser

# Run migrations after model changes
python manage.py makemigrations
python manage.py migrate

# Collect static files (for production)
python manage.py collectstatic

# Run tests
python manage.py test
```

## File Structure

- `tasks/models.py` - Database models
- `tasks/views.py` - View logic
- `tasks/admin.py` - Admin configuration
- `tasks/templates/` - HTML templates
- `static/css/style.css` - Styling
- `todo_project/settings.py` - Project settings

## Need Help?

See README.md for detailed documentation.
