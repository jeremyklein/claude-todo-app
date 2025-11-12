import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo_project.settings')
django.setup()

from django.contrib.auth.models import User
from tasks.models import Category, Task
from datetime import date, timedelta

# Get the admin user
user = User.objects.get(username='admin')

# Create categories
categories_data = [
    {'name': 'Work', 'description': 'Work-related tasks', 'color': '#3498db'},
    {'name': 'Personal', 'description': 'Personal tasks and errands', 'color': '#e74c3c'},
    {'name': 'Health', 'description': 'Health and fitness goals', 'color': '#2ecc71'},
    {'name': 'Learning', 'description': 'Educational and skill development', 'color': '#f39c12'},
    {'name': 'Home', 'description': 'Home maintenance and projects', 'color': '#9b59b6'},
]

categories = {}
for cat_data in categories_data:
    cat, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={
            'description': cat_data['description'],
            'color': cat_data['color']
        }
    )
    categories[cat_data['name']] = cat
    print(f"{'Created' if created else 'Found'} category: {cat.name}")

# Create sample tasks
today = date.today()
tasks_data = [
    {
        'title': 'Review pull requests',
        'description': 'Review and approve pending pull requests from the team',
        'category': 'Work',
        'priority': 3,
        'effort_points': 5,
        'status': 'todo',
        'due_date': today + timedelta(days=2)
    },
    {
        'title': 'Update project documentation',
        'description': 'Update README and API documentation for the latest release',
        'category': 'Work',
        'priority': 2,
        'effort_points': 8,
        'status': 'in_progress',
        'due_date': today + timedelta(days=5)
    },
    {
        'title': 'Grocery shopping',
        'description': 'Buy groceries for the week',
        'category': 'Personal',
        'priority': 2,
        'effort_points': 3,
        'status': 'todo',
        'due_date': today + timedelta(days=1)
    },
    {
        'title': 'Morning workout',
        'description': '30-minute cardio and strength training',
        'category': 'Health',
        'priority': 3,
        'effort_points': 5,
        'status': 'completed',
        'tags': 'exercise, morning'
    },
    {
        'title': 'Learn Django REST Framework',
        'description': 'Complete the DRF tutorial and build a sample API',
        'category': 'Learning',
        'priority': 2,
        'effort_points': 10,
        'status': 'in_progress',
        'due_date': today + timedelta(days=14)
    },
    {
        'title': 'Fix leaky faucet',
        'description': 'Repair the kitchen faucet that has been dripping',
        'category': 'Home',
        'priority': 2,
        'effort_points': 4,
        'status': 'todo',
        'due_date': today + timedelta(days=3)
    },
    {
        'title': 'Prepare presentation',
        'description': 'Create slides for the quarterly review meeting',
        'category': 'Work',
        'priority': 4,
        'effort_points': 7,
        'status': 'todo',
        'due_date': today + timedelta(days=1),
        'tags': 'presentation, urgent'
    },
    {
        'title': 'Read "Clean Code"',
        'description': 'Read chapters 5-8 of Clean Code by Robert Martin',
        'category': 'Learning',
        'priority': 1,
        'effort_points': 6,
        'status': 'todo',
        'tags': 'reading, book'
    },
    {
        'title': 'Dental checkup',
        'description': 'Annual dental cleaning and checkup',
        'category': 'Health',
        'priority': 2,
        'effort_points': 2,
        'status': 'todo',
        'due_date': today + timedelta(days=7)
    },
    {
        'title': 'Complete expense report',
        'description': 'Submit expense report for last month',
        'category': 'Work',
        'priority': 3,
        'effort_points': 3,
        'status': 'completed',
        'tags': 'admin, expenses'
    },
]

for task_data in tasks_data:
    cat_name = task_data.pop('category')
    task, created = Task.objects.get_or_create(
        title=task_data['title'],
        user=user,
        defaults={
            **task_data,
            'category': categories[cat_name]
        }
    )

    # Mark completed tasks properly
    if task_data['status'] == 'completed' and created:
        task.mark_completed()

    print(f"{'Created' if created else 'Found'} task: {task.title}")

print("\nSample data creation complete!")
print(f"Total categories: {Category.objects.count()}")
print(f"Total tasks: {Task.objects.count()}")
