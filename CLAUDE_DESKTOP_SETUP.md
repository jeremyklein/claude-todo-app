# Claude Desktop MCP Setup - Quick Guide

## 5-Minute Setup

### Step 1: Edit Claude Desktop Config

```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### Step 2: Add Configuration

Copy this **exactly** (use your actual paths):

```json
{
  "mcpServers": {
    "django-todo": {
      "command": "/Users/jeremyklein/development/todo-app/venv-mcp/bin/python",
      "args": [
        "/Users/jeremyklein/development/todo-app/mcp_server.py"
      ]
    }
  }
}
```

**For multi-user support**, add the `env` section to specify which Django user:

```json
{
  "mcpServers": {
    "django-todo": {
      "command": "/Users/jeremyklein/development/todo-app/venv-mcp/bin/python",
      "args": [
        "/Users/jeremyklein/development/todo-app/mcp_server.py"
      ],
      "env": {
        "MCP_USER": "your-username"
      }
    }
  }
}
```

See **CLAUDE_DESKTOP_MULTI_USER.md** for complete multi-user setup.

### Step 3: Restart Claude Desktop

**Completely quit** Claude Desktop (Cmd+Q), then reopen it.

### Step 4: Test It!

Try these prompts in Claude Desktop:

```
Show me my todo dashboard
```

```
List my high priority tasks
```

```
Create a task to finish the presentation with 8 effort points, make it urgent
```

## How to Verify It's Working

1. Look for a 🔌 icon or "tools" indicator in Claude Desktop
2. Claude will respond with actual data from your todo database
3. You'll see task lists, effort points, etc.

## What You Can Ask Claude

### Task Management
- "Create a task to [description]"
- "Show me all my todo tasks"
- "List tasks in the Work category"
- "Mark task 7 as completed"
- "Search for tasks about presentation"

### Analytics
- "Show me my dashboard"
- "How many effort points did I earn this week?"
- "Get my analytics for this month"

### Organization
- "List all my categories"
- "Create a new category called Projects"
- "Add a note to task 5"

## Troubleshooting

### "No MCP server found" or tools not showing

**Check 1: Paths are correct**
```bash
# Verify Python path exists
ls /Users/jeremyklein/development/todo-app/venv-mcp/bin/python

# Verify mcp_server.py exists
ls /Users/jeremyklein/development/todo-app/mcp_server.py
```

**Check 2: Virtual environment has dependencies**
```bash
cd /Users/jeremyklein/development/todo-app
source venv-mcp/bin/activate
python -c "import mcp; print('MCP installed')"
```

**Check 3: Config file is valid JSON**
- No trailing commas
- All quotes are double quotes
- All brackets match

**Check 4: Restart Claude Desktop properly**
- Use Cmd+Q to fully quit (not just close window)
- Reopen from Applications

### "Permission denied" errors

```bash
# Make sure files are readable
chmod +x /Users/jeremyklein/development/todo-app/mcp_server.py
```

### MCP server crashes

Check logs:
```bash
# Claude Desktop logs (if available)
tail -f ~/Library/Logs/Claude/mcp*.log
```

Test the server directly:
```bash
cd /Users/jeremyklein/development/todo-app
source venv-mcp/bin/activate
python mcp_server.py
# Try typing: {"jsonrpc": "2.0", "method": "initialize"}
```

## Config File Examples

### If you have multiple MCP servers:

```json
{
  "mcpServers": {
    "django-todo": {
      "command": "/Users/jeremyklein/development/todo-app/venv-mcp/bin/python",
      "args": [
        "/Users/jeremyklein/development/todo-app/mcp_server.py"
      ]
    },
    "another-server": {
      "command": "/path/to/another/server",
      "args": ["--some-arg"]
    }
  }
}
```

### With environment variables:

```json
{
  "mcpServers": {
    "django-todo": {
      "command": "/Users/jeremyklein/development/todo-app/venv-mcp/bin/python",
      "args": [
        "/Users/jeremyklein/development/todo-app/mcp_server.py"
      ],
      "env": {
        "DJANGO_SETTINGS_MODULE": "todo_project.settings"
      }
    }
  }
}
```

## Differences: Claude Desktop vs HTTP Server

| Feature | Claude Desktop (stdio) | HTTP Server |
|---------|----------------------|-------------|
| **Config File** | `claude_desktop_config.json` | Not used |
| **Server File** | `mcp_server.py` | `mcp_server_http.py` |
| **Transport** | stdio | HTTP/SSE |
| **Authentication** | None (local) | Bearer token |
| **Access** | Local only | Remote (web, mobile, API) |
| **Port** | N/A | 8080 |

## Don't Want HTTP Server Running?

If you only use Claude Desktop and don't need remote access, you can:

1. **Stop the HTTP server** (if it's running):
   - The server with process ID showing in terminal
   - Press Ctrl+C or close that terminal

2. **Only use stdio server**:
   - Claude Desktop will automatically start/stop `mcp_server.py` as needed
   - No manual server management required

## Want Both?

You can run BOTH servers simultaneously:
- **stdio server** (`mcp_server.py`) → Auto-started by Claude Desktop
- **HTTP server** (`mcp_server_http.py`) → Run manually for remote access

They both access the same database, so changes in one appear in the other!

## Complete File Reference

Your MCP configuration files:
- `~/Library/Application Support/Claude/claude_desktop_config.json` - Claude Desktop config
- `/Users/jeremyklein/development/todo-app/mcp_server.py` - stdio MCP server (for Claude Desktop)
- `/Users/jeremyklein/development/todo-app/mcp_server_http.py` - HTTP MCP server (for remote access)
- `/Users/jeremyklein/development/todo-app/.env.mcp` - HTTP server configuration

## Getting Help

If Claude Desktop still isn't connecting:

1. Check the config file is valid JSON (paste into jsonlint.com)
2. Verify all paths are absolute (start with `/`)
3. Test the stdio server directly in terminal
4. Look for Claude Desktop logs
5. Try restarting your computer (sometimes helps with process issues)

## Summary

✅ **For Claude Desktop:** Use `mcp_server.py` with stdio transport
✅ **For remote access:** Use `mcp_server_http.py` with HTTP transport
✅ **Both can run simultaneously** and share the same database

Enjoy your AI-powered todo management! 🎉
