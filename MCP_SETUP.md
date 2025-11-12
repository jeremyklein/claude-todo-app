# MCP Server Setup Guide

This guide will help you connect your Django Todo App to Claude using the Model Context Protocol (MCP).

## What is MCP?

MCP (Model Context Protocol) allows Claude to interact directly with your todo app - creating tasks, checking progress, managing categories, and viewing analytics through natural language.

## Prerequisites

- Python 3.10 or higher (MCP requirement)
- Claude Desktop app installed
- Your Django todo app running

## Installation

### 1. The MCP Server is Already Set Up!

The MCP server has been created at `mcp_server.py` and all dependencies are installed in the `venv-mcp` virtual environment.

### 2. Configure Claude Desktop

You need to add the MCP server configuration to Claude Desktop's configuration file.

#### macOS Configuration Location:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

#### Configuration to Add:

Open the file (create it if it doesn't exist) and add this configuration:

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

**Note**: If you already have other MCP servers configured, just add the `django-todo` section to your existing `mcpServers` object.

A template configuration file is available at `claude_desktop_config.json` in this directory.

### 3. Restart Claude Desktop

After adding the configuration, completely quit and restart Claude Desktop for the changes to take effect.

## Available Tools

Once configured, Claude will have access to these tools:

### Task Management
- **create_task** - Create a new task with title, description, category, priority, effort points, due date
- **list_tasks** - List tasks with optional filtering by status, category, priority
- **get_task** - Get full details of a specific task
- **update_task** - Update any field of an existing task
- **complete_task** - Mark a task as completed and record effort points
- **delete_task** - Delete a task
- **search_tasks** - Search tasks by text in title, description, or tags

### Notes
- **add_note** - Add a note to any task

### Analytics
- **get_analytics** - Get effort points and statistics for today/week/month/year
- **get_dashboard** - Get a complete dashboard overview with stats and upcoming tasks

### Categories
- **list_categories** - List all categories
- **create_category** - Create a new category with color

## Usage Examples

Once configured, you can interact with Claude naturally:

### Creating Tasks
```
"Create a task to review the quarterly report with high priority and 8 effort points, due next Friday in the Work category"
```

### Checking Progress
```
"How many effort points have I earned this week?"
```

```
"Show me my dashboard"
```

### Managing Tasks
```
"List all my high priority tasks"
```

```
"Mark task 5 as completed"
```

```
"What tasks do I have in the Health category?"
```

### Analytics
```
"Show me my productivity analytics for this month"
```

```
"What's my effort point breakdown by category?"
```

## Configuration Options

### Change Default User

By default, the MCP server uses the "admin" user. To change this, edit `mcp_server.py`:

```python
# Near the top of the file
DEFAULT_USERNAME = "your_username_here"
```

### Using with Multiple Users

If you want Claude to access tasks for different users, you could:
1. Create separate MCP server configurations for each user
2. Modify the `mcp_server.py` to accept a username parameter
3. Set different environment variables for each configuration

## Troubleshooting

### Claude doesn't show the MCP tools

1. Check that Claude Desktop is completely restarted (quit and reopen)
2. Verify the configuration file path is correct
3. Check the configuration JSON syntax is valid
4. Look at Claude Desktop logs:
   - macOS: `~/Library/Logs/Claude/`

### MCP server errors

1. Verify Python 3.10+ is being used:
   ```bash
   /Users/jeremyklein/development/todo-app/venv-mcp/bin/python --version
   ```

2. Test the MCP server manually:
   ```bash
   source venv-mcp/bin/activate
   python mcp_server.py
   ```

3. Check that the Django database exists:
   ```bash
   ls -la db.sqlite3
   ```

### Permission issues

Make sure the MCP server script is executable:
```bash
chmod +x mcp_server.py
```

## Technical Details

### How It Works

1. Claude Desktop launches the MCP server as a subprocess when it starts
2. The MCP server connects to your Django database (SQLite by default)
3. When you ask Claude to interact with your todos, it calls the appropriate MCP tool
4. The tool executes Django ORM queries and returns results to Claude
5. Claude presents the information to you in natural language

### Database Access

The MCP server accesses the same SQLite database (`db.sqlite3`) as your Django web app. This means:
- Changes made through Claude are immediately visible in the web interface
- Changes made through the web interface are immediately available to Claude
- Both can run simultaneously without conflicts

### Security Considerations

- The MCP server runs locally on your machine
- It has the same database access as your Django web app
- No network traffic or external API calls are made
- All data stays on your local system

## Advanced Usage

### Running with Production Database

If you're using PostgreSQL or MySQL in production:

1. Update the MCP server environment in Claude Desktop config:
   ```json
   "env": {
     "DJANGO_SETTINGS_MODULE": "todo_project.settings",
     "PYTHONPATH": "/Users/jeremyklein/development/todo-app",
     "DATABASE_URL": "postgresql://user:pass@localhost/dbname"
   }
   ```

2. Update Django settings to read from DATABASE_URL

### Custom Tool Development

To add new MCP tools:

1. Add the tool definition in `handle_list_tools()`
2. Add the handler in `handle_call_tool()`
3. Implement the async function
4. Restart Claude Desktop

Example tool structure:
```python
@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="my_custom_tool",
            description="What this tool does",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "Parameter description"}
                },
                "required": ["param"]
            }
        )
    ]

async def my_custom_tool(user: User, args: dict) -> list[TextContent]:
    # Implementation
    result = {"status": "success"}
    return [TextContent(type="text", text=json.dumps(result, indent=2))]
```

## Testing the MCP Server

### Manual Testing

You can test the MCP server independently:

```bash
source venv-mcp/bin/activate
python mcp_server.py
```

### Testing with Inspector

Use the MCP Inspector tool (if available) to test tools without Claude Desktop.

### Debugging

Add logging to the MCP server:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Considerations

- The MCP server is lightweight and fast
- Database queries are optimized with Django ORM
- Typical response time: < 100ms for most operations
- No performance impact on the Django web server

## Next Steps

1. Configure Claude Desktop with the provided settings
2. Restart Claude Desktop
3. Try asking Claude: "Show me my todo dashboard"
4. Create tasks, check analytics, and manage your todos through conversation!

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Claude Desktop](https://claude.ai/download)

## Support

If you encounter issues:
1. Check this documentation
2. Review the troubleshooting section
3. Check Claude Desktop logs
4. Verify Python and Django versions
5. Test the MCP server manually

Enjoy managing your todos with Claude!
