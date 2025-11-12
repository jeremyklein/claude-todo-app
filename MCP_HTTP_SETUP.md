# HTTP MCP Server Setup Guide

## Overview

The HTTP MCP Server provides remote access to your Django Todo App via the Model Context Protocol (MCP) over HTTP/SSE transport. This enables access from:
- Claude AI API (not just Claude Desktop)
- Web applications
- Mobile apps
- Any HTTP client supporting MCP protocol

## Quick Start

### 1. Start the HTTP MCP Server

```bash
cd /Users/jeremyklein/development/todo-app
source venv-mcp/bin/activate
python mcp_server_http.py
```

The server will start on `http://0.0.0.0:8080` by default.

### 2. Configure Authentication

The server uses Bearer token authentication. The default token is configured in `.env.mcp`:

```bash
MCP_AUTH_TOKEN=mcp-secret-token-change-me-in-production
```

**IMPORTANT:** Change this token in production!

### 3. Test the Server

```bash
# Health check
curl http://localhost:8080/health

# Server info
curl http://localhost:8080/

# Test MCP protocol
curl -X POST http://localhost:8080/messages \
  -H "Authorization: Bearer mcp-secret-token-change-me-in-production" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}'
```

## Server Endpoints

### GET /
**Description:** Server information and available tools

**Response:**
```json
{
  "name": "Django Todo MCP Server (HTTP)",
  "version": "1.0.0",
  "protocol": "mcp",
  "transport": "sse",
  "tools": ["create_task", "list_tasks", "get_task", ...]
}
```

### GET /health
**Description:** Health check endpoint

**Response:**
```json
{"status": "healthy", "server": "django-todo-mcp-http"}
```

### GET /sse
**Description:** Server-Sent Events endpoint for MCP notifications

**Headers:**
- `Authorization: Bearer <token>` (required)

**Response:** SSE stream with MCP server events

### POST /messages
**Description:** Main MCP JSON-RPC endpoint for tool calls

**Headers:**
- `Authorization: Bearer <token>` (required)
- `Content-Type: application/json`

**Request Format:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "<mcp_method>",
  "params": {<method_parameters>}
}
```

**Response Format:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {<method_result>}
}
```

## MCP Protocol Methods

### initialize
Initialize the MCP connection

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {}
}
```

### tools/list
Get list of available tools

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

### tools/call
Execute a tool

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "create_task",
    "arguments": {
      "title": "My task",
      "priority": 3,
      "effort_points": 5
    }
  }
}
```

## Available Tools

The HTTP MCP server provides all 12 tools from the stdio version:

1. **create_task** - Create a new task
2. **list_tasks** - List tasks with optional filtering
3. **get_task** - Get details of a specific task
4. **update_task** - Update an existing task
5. **complete_task** - Mark a task as completed
6. **delete_task** - Delete a task
7. **add_note** - Add a note to a task
8. **get_analytics** - Get effort points analytics
9. **list_categories** - List all categories
10. **create_category** - Create a new category
11. **get_dashboard** - Get dashboard overview
12. **search_tasks** - Search tasks by text

## Tool Usage Examples

### Create a Task
```bash
curl -X POST http://localhost:8080/messages \
  -H "Authorization: Bearer mcp-secret-token-change-me-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "create_task",
      "arguments": {
        "title": "Finish presentation",
        "description": "Complete slides for next week",
        "category": "Work",
        "priority": 3,
        "effort_points": 8,
        "due_date": "2025-11-20",
        "tags": "urgent,presentation"
      }
    }
  }'
```

### List Tasks
```bash
curl -X POST http://localhost:8080/messages \
  -H "Authorization: Bearer mcp-secret-token-change-me-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "list_tasks",
      "arguments": {
        "status": "todo",
        "priority": 3,
        "limit": 10
      }
    }
  }'
```

### Complete a Task
```bash
curl -X POST http://localhost:8080/messages \
  -H "Authorization: Bearer mcp-secret-token-change-me-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "complete_task",
      "arguments": {
        "task_id": 7
      }
    }
  }'
```

### Search Tasks
```bash
curl -X POST http://localhost:8080/messages \
  -H "Authorization: Bearer mcp-secret-token-change-me-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "search_tasks",
      "arguments": {
        "query": "presentation",
        "limit": 5
      }
    }
  }'
```

### Get Dashboard
```bash
curl -X POST http://localhost:8080/messages \
  -H "Authorization: Bearer mcp-secret-token-change-me-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "get_dashboard",
      "arguments": {}
    }
  }'
```

### Get Analytics
```bash
curl -X POST http://localhost:8080/messages \
  -H "Authorization: Bearer mcp-secret-token-change-me-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 6,
    "method": "tools/call",
    "params": {
      "name": "get_analytics",
      "arguments": {
        "period": "week"
      }
    }
  }'
```

## Configuration

Configuration is stored in `.env.mcp`:

```bash
# Server settings
MCP_HOST=0.0.0.0          # Host to bind to
MCP_PORT=8080             # Port to listen on

# Authentication
MCP_AUTH_TOKEN=mcp-secret-token-change-me-in-production

# Django settings
MCP_USER=admin            # Django user for operations
DJANGO_SETTINGS_MODULE=todo_project.settings
```

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8080"
TOKEN = "mcp-secret-token-change-me-in-production"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Initialize
response = requests.post(
    f"{BASE_URL}/messages",
    headers=headers,
    json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    }
)
print(response.json())

# Create a task
response = requests.post(
    f"{BASE_URL}/messages",
    headers=headers,
    json={
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "create_task",
            "arguments": {
                "title": "My new task",
                "priority": 2,
                "effort_points": 5
            }
        }
    }
)
result = response.json()
print(result["result"]["content"][0]["text"])
```

## JavaScript Client Example

```javascript
const BASE_URL = 'http://localhost:8080';
const TOKEN = 'mcp-secret-token-change-me-in-production';

async function callMCPTool(toolName, arguments) {
  const response = await fetch(`${BASE_URL}/messages`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${TOKEN}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: Date.now(),
      method: 'tools/call',
      params: {
        name: toolName,
        arguments: arguments
      }
    })
  });

  const data = await response.json();
  return data.result.content[0].text;
}

// Usage
const result = await callMCPTool('list_tasks', {
  status: 'todo',
  limit: 5
});
console.log(result);
```

## Security Considerations

### Production Deployment

1. **Change the authentication token:**
   ```bash
   # Generate a strong token
   openssl rand -hex 32

   # Update .env.mcp
   MCP_AUTH_TOKEN=<your-strong-token>
   ```

2. **Use HTTPS:**
   - Deploy behind a reverse proxy (nginx, Apache)
   - Use SSL certificates (Let's Encrypt)
   - Update CORS settings for your domain

3. **Restrict CORS:**
   ```python
   # In mcp_server_http.py, update CORS middleware:
   allow_origins=["https://your-domain.com"]
   ```

4. **Rate limiting:**
   - Implement rate limiting at reverse proxy level
   - Use tools like nginx `limit_req` module

5. **Firewall:**
   - Only expose the server to trusted networks
   - Use firewall rules to restrict access

## Troubleshooting

### Server won't start
- Check if port 8080 is already in use: `lsof -i :8080`
- Verify virtual environment is activated: `which python`
- Check Django dependencies are installed in venv-mcp

### Authentication errors
- Verify token in .env.mcp matches the request
- Check Authorization header format: `Bearer <token>`
- Ensure .env.mcp is being loaded (check server logs)

### Tool execution errors
- Check server logs for detailed error messages
- Verify Django database is accessible
- Ensure admin user exists in database

### CORS errors
- Update CORS middleware `allow_origins` in mcp_server_http.py
- Check browser console for specific CORS errors

## Differences from stdio MCP Server

| Feature | stdio (mcp_server.py) | HTTP (mcp_server_http.py) |
|---------|----------------------|---------------------------|
| **Transport** | stdio | HTTP/SSE |
| **Access** | Local only (Claude Desktop) | Remote (web, mobile, API) |
| **Authentication** | None | Bearer token |
| **Port** | N/A | 8080 (configurable) |
| **Tools** | 12 tools | 12 tools (same) |
| **Database** | Direct Django ORM | Direct Django ORM (same) |
| **Deployment** | Configured in Claude Desktop | Run as HTTP service |

## Integration with Claude API

You can connect Claude AI API to your HTTP MCP server:

1. Set up the HTTP server on a public URL (with HTTPS)
2. Configure Claude API to use your MCP server endpoint
3. Provide authentication token
4. Claude API can now access all 12 tools remotely

## Next Steps

- Deploy to a cloud service (AWS, Google Cloud, Azure)
- Set up HTTPS with SSL certificates
- Implement request logging and monitoring
- Add webhooks for task notifications
- Create a web frontend using the MCP server

## Support

For issues or questions:
- Check server logs for detailed error messages
- Review Django logs: `python manage.py runserver` output
- Verify token authentication is working correctly

## Summary

✅ **HTTP MCP Server is now fully operational!**

- 12 tools available remotely
- Bearer token authentication
- Full MCP protocol support
- Same Django database as stdio server and REST API
- Ready for web/mobile integration

The HTTP MCP server complements the existing stdio server (for Claude Desktop) and REST API, giving you three ways to access your todo app!
