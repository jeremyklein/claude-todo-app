#!/usr/bin/env python3
"""
Test MCP server startup and Django connection
"""
import os
import sys

print("=" * 60)
print("MCP Server Startup Test")
print("=" * 60)

# Test 1: Python version
print(f"\n1. Python version: {sys.version}")
if sys.version_info < (3, 10):
    print("   ❌ ERROR: Need Python 3.10+")
    sys.exit(1)
print("   ✓ Python version OK")

# Test 2: Working directory
print(f"\n2. Working directory: {os.getcwd()}")

# Test 3: PYTHONPATH
pythonpath = os.environ.get('PYTHONPATH', 'Not set')
print(f"3. PYTHONPATH: {pythonpath}")

# Test 4: Django setup
print("\n4. Testing Django setup...")
try:
    sys.path.insert(0, '/Users/jeremyklein/development/todo-app')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo_project.settings')
    import django
    django.setup()
    print("   ✓ Django imported and configured")
except Exception as e:
    print(f"   ❌ Django setup failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Database connection
print("\n5. Testing database connection...")
try:
    from django.contrib.auth.models import User
    from tasks.models import Task
    user_count = User.objects.count()
    task_count = Task.objects.count()
    print(f"   ✓ Database connected: {user_count} users, {task_count} tasks")
except Exception as e:
    print(f"   ❌ Database connection failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: MCP imports
print("\n6. Testing MCP imports...")
try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    print("   ✓ MCP modules imported successfully")
except Exception as e:
    print(f"   ❌ MCP import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: Try to create the server
print("\n7. Testing MCP server creation...")
try:
    app = Server("django-todo-mcp")
    print("   ✓ MCP server created successfully")
except Exception as e:
    print(f"   ❌ Server creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED - MCP server should work!")
print("=" * 60)
print("\nIf Claude Desktop still has issues, check:")
print("1. Claude Desktop logs: ~/Library/Logs/Claude/")
print("2. Completely quit and restart Claude Desktop")
print("3. Try removing and re-adding the MCP configuration")
