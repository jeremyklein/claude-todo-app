#!/usr/bin/env python3
"""
MCP Server for Django Todo App
Allows Claude to interact with your todo application through MCP protocol
"""

import os
import sys
import json
import asyncio
from datetime import datetime, date, timedelta
from typing import Any, Optional

# Add the Django project to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo_project.settings')
import django
django.setup()

from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from tasks.models import Task, Category, TaskCompletion, Note
from asgiref.sync import sync_to_async

# MCP imports
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Create MCP server
app = Server("django-todo-mcp")

# Default user (can be configured)
DEFAULT_USERNAME = "admin"


def get_user() -> User:
    """Get the default user for operations"""
    try:
        return User.objects.get(username=DEFAULT_USERNAME)
    except User.DoesNotExist:
        # Try to get the first superuser
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            raise Exception(f"No user found. Please create a user with username '{DEFAULT_USERNAME}' or configure DEFAULT_USERNAME")
        return user


def serialize_date(obj):
    """JSON serializer for dates"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools for the todo app"""
    return [
        Tool(
            name="create_task",
            description="Create a new task with title, description, category, priority, effort points, and optional due date",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Task title"
                    },
                    "description": {
                        "type": "string",
                        "description": "Task description (optional)"
                    },
                    "category": {
                        "type": "string",
                        "description": "Category name (optional)"
                    },
                    "priority": {
                        "type": "integer",
                        "description": "Priority level: 1 (Low), 2 (Medium), 3 (High), 4 (Urgent)",
                        "enum": [1, 2, 3, 4]
                    },
                    "effort_points": {
                        "type": "integer",
                        "description": "Effort points (1-10)",
                        "minimum": 1,
                        "maximum": 10
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Due date in YYYY-MM-DD format (optional)"
                    },
                    "tags": {
                        "type": "string",
                        "description": "Comma-separated tags (optional)"
                    },
                    "status": {
                        "type": "string",
                        "description": "Task status (optional, defaults to 'todo')",
                        "enum": ["todo", "in_progress", "completed", "archived"]
                    }
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="list_tasks",
            description="List tasks with optional filtering by status, category, or priority",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Filter by status",
                        "enum": ["todo", "in_progress", "completed", "archived"]
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by category name"
                    },
                    "priority": {
                        "type": "integer",
                        "description": "Filter by priority (1-4)",
                        "enum": [1, 2, 3, 4]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of tasks to return (default: 20)",
                        "default": 20
                    }
                }
            }
        ),
        Tool(
            name="get_task",
            description="Get details of a specific task by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "Task ID"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="update_task",
            description="Update an existing task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "Task ID"
                    },
                    "title": {
                        "type": "string",
                        "description": "New task title"
                    },
                    "description": {
                        "type": "string",
                        "description": "New task description"
                    },
                    "category": {
                        "type": "string",
                        "description": "New category name"
                    },
                    "priority": {
                        "type": "integer",
                        "description": "New priority level (1-4)",
                        "enum": [1, 2, 3, 4]
                    },
                    "effort_points": {
                        "type": "integer",
                        "description": "New effort points (1-10)",
                        "minimum": 1,
                        "maximum": 10
                    },
                    "status": {
                        "type": "string",
                        "description": "New status",
                        "enum": ["todo", "in_progress", "completed", "archived"]
                    },
                    "due_date": {
                        "type": "string",
                        "description": "New due date in YYYY-MM-DD format"
                    },
                    "tags": {
                        "type": "string",
                        "description": "New tags (comma-separated)"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="complete_task",
            description="Mark a task as completed and record effort points",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "Task ID"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="delete_task",
            description="Delete a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "Task ID"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="add_note",
            description="Add a note to a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "Task ID"
                    },
                    "content": {
                        "type": "string",
                        "description": "Note content"
                    }
                },
                "required": ["task_id", "content"]
            }
        ),
        Tool(
            name="get_analytics",
            description="Get effort points and task analytics",
            inputSchema={
                "type": "object",
                "properties": {
                    "period": {
                        "type": "string",
                        "description": "Time period to analyze",
                        "enum": ["today", "week", "month", "year", "all"]
                    }
                }
            }
        ),
        Tool(
            name="list_categories",
            description="List all available categories",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="create_category",
            description="Create a new category",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Category name"
                    },
                    "description": {
                        "type": "string",
                        "description": "Category description (optional)"
                    },
                    "color": {
                        "type": "string",
                        "description": "Hex color code (e.g., #3498db, optional)"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="get_dashboard",
            description="Get dashboard overview with stats, upcoming tasks, and overdue tasks",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="search_tasks",
            description="Search tasks by text in title, description, or tags",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 20)",
                        "default": 20
                    }
                },
                "required": ["query"]
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    try:
        user = await sync_to_async(get_user)()

        if name == "create_task":
            return await create_task(user, arguments)
        elif name == "list_tasks":
            return await list_tasks(user, arguments)
        elif name == "get_task":
            return await get_task(user, arguments)
        elif name == "update_task":
            return await update_task(user, arguments)
        elif name == "complete_task":
            return await complete_task(user, arguments)
        elif name == "delete_task":
            return await delete_task(user, arguments)
        elif name == "add_note":
            return await add_note(user, arguments)
        elif name == "get_analytics":
            return await get_analytics(user, arguments)
        elif name == "list_categories":
            return await list_categories()
        elif name == "create_category":
            return await create_category(arguments)
        elif name == "get_dashboard":
            return await get_dashboard(user)
        elif name == "search_tasks":
            return await search_tasks(user, arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return [TextContent(type="text", text=f"Error: {str(e)}\n\n{error_details}")]


async def create_task(user: User, args: dict) -> list[TextContent]:
    """Create a new task"""
    title = args["title"]
    description = args.get("description", "")
    category_name = args.get("category")
    priority = args.get("priority", 2)
    effort_points = args.get("effort_points", 1)
    due_date_str = args.get("due_date")
    tags = args.get("tags", "")
    status = args.get("status", "todo")

    # Get or create category
    category = None
    if category_name:
        category, _ = Category.objects.get_or_create(name=category_name)

    # Parse due date
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            return [TextContent(type="text", text=f"Invalid date format. Use YYYY-MM-DD")]

    # Create task
    task = Task.objects.create(
        title=title,
        description=description,
        category=category,
        priority=priority,
        effort_points=effort_points,
        due_date=due_date,
        tags=tags,
        status=status,
        user=user
    )

    result = {
        "id": task.id,
        "title": task.title,
        "status": task.status,
        "priority": task.get_priority_display(),
        "effort_points": task.effort_points,
        "category": task.category.name if task.category else None,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "created_at": task.created_at.isoformat()
    }

    return [TextContent(type="text", text=f"Task created successfully!\n\n{json.dumps(result, indent=2)}")]


async def list_tasks(user: User, args: dict) -> list[TextContent]:
    """List tasks with optional filtering"""
    queryset = Task.objects.filter(user=user)

    # Apply filters
    if "status" in args:
        queryset = queryset.filter(status=args["status"])
    if "category" in args:
        queryset = queryset.filter(category__name=args["category"])
    if "priority" in args:
        queryset = queryset.filter(priority=args["priority"])

    # Limit results
    limit = args.get("limit", 20)
    tasks = queryset.order_by('-priority', 'due_date')[:limit]

    if not tasks:
        return [TextContent(type="text", text="No tasks found.")]

    result = []
    for task in tasks:
        result.append({
            "id": task.id,
            "title": task.title,
            "status": task.status,
            "priority": task.get_priority_display(),
            "effort_points": task.effort_points,
            "category": task.category.name if task.category else None,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "tags": task.tags
        })

    return [TextContent(type="text", text=f"Found {len(result)} tasks:\n\n{json.dumps(result, indent=2, default=serialize_date)}")]


async def get_task(user: User, args: dict) -> list[TextContent]:
    """Get details of a specific task"""
    task_id = args["task_id"]

    try:
        task = Task.objects.get(id=task_id, user=user)
    except Task.DoesNotExist:
        return [TextContent(type="text", text=f"Task {task_id} not found.")]

    # Get notes
    notes = list(task.notes.values('id', 'content', 'created_at'))

    result = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.get_priority_display(),
        "effort_points": task.effort_points,
        "category": task.category.name if task.category else None,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "tags": task.tags,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "notes": notes
    }

    return [TextContent(type="text", text=json.dumps(result, indent=2, default=serialize_date))]


async def update_task(user: User, args: dict) -> list[TextContent]:
    """Update an existing task"""
    task_id = args["task_id"]

    try:
        task = Task.objects.get(id=task_id, user=user)
    except Task.DoesNotExist:
        return [TextContent(type="text", text=f"Task {task_id} not found.")]

    # Update fields
    if "title" in args:
        task.title = args["title"]
    if "description" in args:
        task.description = args["description"]
    if "priority" in args:
        task.priority = args["priority"]
    if "effort_points" in args:
        task.effort_points = args["effort_points"]
    if "status" in args:
        task.status = args["status"]
        if args["status"] == "completed" and not task.completed_at:
            task.mark_completed()
            return [TextContent(type="text", text=f"Task '{task.title}' marked as completed and effort points recorded!")]
    if "tags" in args:
        task.tags = args["tags"]
    if "category" in args:
        category, _ = Category.objects.get_or_create(name=args["category"])
        task.category = category
    if "due_date" in args:
        try:
            task.due_date = datetime.strptime(args["due_date"], "%Y-%m-%d").date()
        except ValueError:
            return [TextContent(type="text", text=f"Invalid date format. Use YYYY-MM-DD")]

    task.save()

    return [TextContent(type="text", text=f"Task '{task.title}' updated successfully!")]


async def complete_task(user: User, args: dict) -> list[TextContent]:
    """Mark a task as completed"""
    task_id = args["task_id"]

    try:
        task = Task.objects.get(id=task_id, user=user)
    except Task.DoesNotExist:
        return [TextContent(type="text", text=f"Task {task_id} not found.")]

    if task.status == "completed":
        return [TextContent(type="text", text=f"Task '{task.title}' is already completed.")]

    task.mark_completed()

    return [TextContent(type="text", text=f"Task '{task.title}' completed! Earned {task.effort_points} effort points.")]


async def delete_task(user: User, args: dict) -> list[TextContent]:
    """Delete a task"""
    task_id = args["task_id"]

    try:
        task = Task.objects.get(id=task_id, user=user)
    except Task.DoesNotExist:
        return [TextContent(type="text", text=f"Task {task_id} not found.")]

    title = task.title
    task.delete()

    return [TextContent(type="text", text=f"Task '{title}' deleted successfully.")]


async def add_note(user: User, args: dict) -> list[TextContent]:
    """Add a note to a task"""
    task_id = args["task_id"]
    content = args["content"]

    try:
        task = Task.objects.get(id=task_id, user=user)
    except Task.DoesNotExist:
        return [TextContent(type="text", text=f"Task {task_id} not found.")]

    note = Note.objects.create(
        task=task,
        user=user,
        content=content
    )

    return [TextContent(type="text", text=f"Note added to task '{task.title}'.")]


async def get_analytics(user: User, args: dict) -> list[TextContent]:
    """Get analytics and effort points"""
    period = args.get("period", "all")
    today = date.today()

    result = {
        "total_tasks": Task.objects.filter(user=user).count(),
        "completed_tasks": Task.objects.filter(user=user, status="completed").count(),
    }

    if period in ["today", "all"]:
        result["points_today"] = TaskCompletion.get_daily_points(user, today)

    if period in ["week", "all"]:
        result["points_this_week"] = TaskCompletion.get_weekly_points(user, today)

    if period in ["month", "all"]:
        result["points_this_month"] = TaskCompletion.get_monthly_points(user, today)

    if period in ["year", "all"]:
        result["points_this_year"] = TaskCompletion.get_yearly_points(user, today)

    if period == "all":
        result["total_points_earned"] = TaskCompletion.objects.filter(user=user).aggregate(
            total=Sum('effort_points')
        )['total'] or 0

        # Category breakdown
        category_stats = TaskCompletion.objects.filter(user=user).values(
            'task__category__name'
        ).annotate(
            total_points=Sum('effort_points'),
            task_count=Count('id')
        ).order_by('-total_points')

        result["category_breakdown"] = list(category_stats)

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def list_categories() -> list[TextContent]:
    """List all categories"""
    categories = Category.objects.all().order_by('name')

    if not categories:
        return [TextContent(type="text", text="No categories found.")]

    result = []
    for cat in categories:
        result.append({
            "id": cat.id,
            "name": cat.name,
            "description": cat.description,
            "color": cat.color,
            "task_count": cat.tasks.count()
        })

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def create_category(args: dict) -> list[TextContent]:
    """Create a new category"""
    name = args["name"]
    description = args.get("description", "")
    color = args.get("color", "#3498db")

    category, created = Category.objects.get_or_create(
        name=name,
        defaults={"description": description, "color": color}
    )

    if not created:
        return [TextContent(type="text", text=f"Category '{name}' already exists.")]

    return [TextContent(type="text", text=f"Category '{name}' created successfully!")]


async def get_dashboard(user: User) -> list[TextContent]:
    """Get dashboard overview"""
    today = date.today()

    # Get tasks
    tasks_todo = Task.objects.filter(user=user, status='todo').count()
    tasks_in_progress = Task.objects.filter(user=user, status='in_progress').count()
    tasks_completed_today = Task.objects.filter(
        user=user,
        status='completed',
        completed_at__date=today
    ).count()

    # Get effort points
    points_today = TaskCompletion.get_daily_points(user, today)
    points_week = TaskCompletion.get_weekly_points(user, today)
    points_month = TaskCompletion.get_monthly_points(user, today)
    points_year = TaskCompletion.get_yearly_points(user, today)

    # Get upcoming tasks
    upcoming_deadline = today + timedelta(days=7)
    upcoming_tasks = Task.objects.filter(
        user=user,
        status__in=['todo', 'in_progress'],
        due_date__gte=today,
        due_date__lte=upcoming_deadline
    ).values('id', 'title', 'due_date', 'priority', 'effort_points')

    # Get overdue tasks
    overdue_tasks = Task.objects.filter(
        user=user,
        status__in=['todo', 'in_progress'],
        due_date__lt=today
    ).values('id', 'title', 'due_date', 'priority', 'effort_points')

    result = {
        "effort_points": {
            "today": points_today,
            "this_week": points_week,
            "this_month": points_month,
            "this_year": points_year
        },
        "task_counts": {
            "todo": tasks_todo,
            "in_progress": tasks_in_progress,
            "completed_today": tasks_completed_today
        },
        "upcoming_tasks": list(upcoming_tasks),
        "overdue_tasks": list(overdue_tasks)
    }

    return [TextContent(type="text", text=json.dumps(result, indent=2, default=serialize_date))]


async def search_tasks(user: User, args: dict) -> list[TextContent]:
    """Search tasks"""
    query = args["query"]
    limit = args.get("limit", 20)

    tasks = Task.objects.filter(
        user=user
    ).filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(tags__icontains=query)
    )[:limit]

    if not tasks:
        return [TextContent(type="text", text=f"No tasks found matching '{query}'.")]

    result = []
    for task in tasks:
        result.append({
            "id": task.id,
            "title": task.title,
            "description": task.description[:100] + "..." if len(task.description) > 100 else task.description,
            "status": task.status,
            "priority": task.get_priority_display(),
            "effort_points": task.effort_points,
            "category": task.category.name if task.category else None
        })

    return [TextContent(type="text", text=f"Found {len(result)} tasks matching '{query}':\n\n{json.dumps(result, indent=2)}")]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="django-todo-mcp",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
