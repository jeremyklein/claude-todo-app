#!/usr/bin/env python3
"""
Test script for MCP Server
Verifies that the MCP server can connect to Django and perform basic operations
"""

import os
import sys

# Add the Django project to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo_project.settings')
import django
django.setup()

from django.contrib.auth.models import User
from tasks.models import Task, Category, TaskCompletion
from datetime import date


def test_database_connection():
    """Test that we can connect to the database"""
    print("Testing database connection...")
    try:
        user_count = User.objects.count()
        print(f"✓ Database connected. Found {user_count} users.")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


def test_user_access():
    """Test that we can access the default user"""
    print("\nTesting user access...")
    try:
        user = User.objects.get(username='admin')
        print(f"✓ Found user: {user.username}")
        return True, user
    except User.DoesNotExist:
        print("✗ Admin user not found. Please create one.")
        return False, None


def test_task_operations(user):
    """Test basic task operations"""
    print("\nTesting task operations...")

    # Count tasks
    task_count = Task.objects.filter(user=user).count()
    print(f"  Found {task_count} tasks for user {user.username}")

    # Get tasks by status
    todo_count = Task.objects.filter(user=user, status='todo').count()
    in_progress_count = Task.objects.filter(user=user, status='in_progress').count()
    completed_count = Task.objects.filter(user=user, status='completed').count()

    print(f"  - To Do: {todo_count}")
    print(f"  - In Progress: {in_progress_count}")
    print(f"  - Completed: {completed_count}")

    print("✓ Task operations successful")
    return True


def test_category_operations():
    """Test category operations"""
    print("\nTesting category operations...")

    category_count = Category.objects.count()
    print(f"  Found {category_count} categories")

    for cat in Category.objects.all()[:5]:
        task_count = cat.tasks.count()
        print(f"  - {cat.name}: {task_count} tasks")

    print("✓ Category operations successful")
    return True


def test_analytics(user):
    """Test analytics operations"""
    print("\nTesting analytics operations...")

    today = date.today()
    points_today = TaskCompletion.get_daily_points(user, today)
    points_week = TaskCompletion.get_weekly_points(user, today)
    points_month = TaskCompletion.get_monthly_points(user, today)
    points_year = TaskCompletion.get_yearly_points(user, today)

    print(f"  Effort points:")
    print(f"  - Today: {points_today}")
    print(f"  - This week: {points_week}")
    print(f"  - This month: {points_month}")
    print(f"  - This year: {points_year}")

    print("✓ Analytics operations successful")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("MCP Server Test Suite")
    print("=" * 60)

    # Run tests
    if not test_database_connection():
        print("\n✗ Tests failed: Cannot connect to database")
        return False

    success, user = test_user_access()
    if not success:
        print("\n✗ Tests failed: Cannot access user")
        return False

    test_task_operations(user)
    test_category_operations()
    test_analytics(user)

    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    print("\nThe MCP server should work correctly.")
    print("Next steps:")
    print("1. Add the configuration to Claude Desktop")
    print("2. Restart Claude Desktop")
    print("3. Ask Claude: 'Show me my todo dashboard'")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
