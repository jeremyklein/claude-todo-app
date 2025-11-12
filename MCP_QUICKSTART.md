# MCP Quick Start - Connect Claude to Your Todo App

## 5-Minute Setup

### Step 1: Copy Configuration

1. Open (or create) the Claude Desktop config file:
   ```bash
   nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. Add this configuration (or merge with existing `mcpServers`):
   ```json
   {
     "mcpServers": {
       "django-todo": {
         "command": "/Users/jeremyklein/development/todo-app/venv-mcp/bin/python",
         "args": [
           "/Users/jeremyklein/development/todo-app/mcp_server.py"
         ],
         "env": {
           "DJANGO_SETTINGS_MODULE": "todo_project.settings",
           "PYTHONPATH": "/Users/jeremyklein/development/todo-app"
         }
       }
     }
   }
   ```

### Step 2: Restart Claude Desktop

Completely quit Claude Desktop (Cmd+Q) and reopen it.

### Step 3: Test It!

In Claude Desktop, try these commands:

```
"Show me my todo dashboard"
"Create a task to review the project plan with high priority and 5 effort points"
"How many effort points have I earned this week?"
"List all my tasks"
```

## What You Can Do

### Task Management
- Create tasks with priorities, categories, and effort points
- List and filter tasks by status, category, or priority
- Update and complete tasks
- Delete tasks
- Search tasks by keywords

### Progress Tracking
- View effort points for today/week/month/year
- Get dashboard overview
- Check analytics and category breakdowns

### Organization
- Create and manage categories
- Add notes to tasks
- Tag tasks for easy searching

## Example Conversations

**Create a Task:**
> "Create a task called 'Prepare quarterly report' in the Work category with high priority, 8 effort points, and make it due next Friday"

**Check Progress:**
> "How am I doing this week? Show me my effort points and upcoming tasks"

**Manage Tasks:**
> "Show me all urgent tasks in the Work category"
> "Mark task 7 as completed"

**Get Analytics:**
> "What's my productivity been like this month?"
> "Show me which categories I've been focusing on"

## Troubleshooting

### Tools not showing in Claude?
1. Make sure you completely quit and restarted Claude Desktop
2. Check the config file path and JSON syntax
3. Verify the Python path in the config matches your setup

### Want to test manually?
```bash
cd /Users/jeremyklein/development/todo-app
source venv-mcp/bin/activate
python test_mcp.py
```

## Next Steps

- Read MCP_SETUP.md for detailed documentation
- Customize the MCP server for your workflow
- Add custom tools for specialized features

Enjoy using Claude to manage your todos!
