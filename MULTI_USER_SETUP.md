# Multi-User MCP Server Setup

## Problem Solved

By default, the MCP servers use a single user (`admin`). This means all tasks are associated with that one user. With multi-user support, **each token maps to a specific Django user**, ensuring each user only sees their own tasks.

## How It Works

### HTTP MCP Server (Multi-User Support) ✅

The HTTP MCP server (`mcp_server_http.py`) now supports multiple users through token-based authentication:

1. Each authentication token maps to a specific Django user
2. When a request comes in, the token is validated
3. The token is mapped to a user
4. All tasks are filtered to that user's data only

### stdio MCP Server (Single User)

The stdio server (`mcp_server.py`) for Claude Desktop remains single-user by design, as it's meant for personal desktop use.

## Setup Multi-User Authentication

### Step 1: Create Django Users

First, create users in your Django database:

```bash
cd /Users/jeremyklein/development/todo-app
source venv/bin/activate
python manage.py shell
```

```python
from django.contrib.auth.models import User

# Create users
alice = User.objects.create_user('alice', 'alice@example.com', 'alice_password')
bob = User.objects.create_user('bob', 'bob@example.com', 'bob_password')
charlie = User.objects.create_user('charlie', 'charlie@example.com', 'charlie_password')

print("Users created!")
```

### Step 2: Generate Tokens for Each User

Generate secure tokens for each user:

```bash
# Generate secure tokens
openssl rand -hex 32  # For alice
openssl rand -hex 32  # For bob
openssl rand -hex 32  # For charlie
```

Example output:
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6  # alice's token
z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5k4  # bob's token
m5n6o7p8q9r0s1t2u3v4w5x6y7z8a9b0  # charlie's token
```

### Step 3: Configure Token Mapping

Edit `.env.mcp` and add the token-to-user mapping:

```bash
# Multi-user support: Map tokens to specific users
# Format: token1:username1,token2:username2,token3:username3
MCP_TOKEN_USER_MAPPING=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6:alice,z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5k4:bob,m5n6o7p8q9r0s1t2u3v4w5x6y7z8a9b0:charlie
```

**Important:** Don't add spaces around the colons or commas.

### Step 4: Restart the HTTP MCP Server

```bash
# Kill the current server (Ctrl+C if running in foreground)
# Or find and kill the process

# Start the new server
cd /Users/jeremyklein/development/todo-app
source venv-mcp/bin/activate
python mcp_server_http.py
```

### Step 5: Test Multi-User Access

Now each user can access only their own tasks:

**Alice's requests:**
```bash
curl -X POST http://localhost:8080/messages \
  -H "Authorization: Bearer a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "list_tasks",
      "arguments": {"limit": 5}
    }
  }'
```

**Bob's requests:**
```bash
curl -X POST http://localhost:8080/messages \
  -H "Authorization: Bearer z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5k4" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "create_task",
      "arguments": {
        "title": "Bob's task",
        "priority": 2,
        "effort_points": 3
      }
    }
  }'
```

**Charlie's requests:**
```bash
curl -X POST http://localhost:8080/messages \
  -H "Authorization: Bearer m5n6o7p8q9r0s1t2u3v4w5x6y7z8a9b0" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "get_dashboard",
      "arguments": {}
    }
  }'
```

## Verification

You can verify multi-user authentication is working by checking the server logs:

```bash
# You should see logs like:
INFO:__main__:Authenticated as user: alice
INFO:__main__:Received MCP request: tools/call from user: alice

INFO:__main__:Authenticated as user: bob
INFO:__main__:Received MCP request: tools/call from user: bob
```

## Data Isolation

Each user's data is completely isolated:

- **Alice** can only see/modify Alice's tasks
- **Bob** can only see/modify Bob's tasks
- **Charlie** can only see/modify Charlie's tasks

This applies to:
- ✅ Tasks (list, create, update, delete, complete)
- ✅ Dashboard (only shows user's stats)
- ✅ Analytics (only user's effort points)
- ✅ Search (only searches user's tasks)
- ✅ Notes (only on user's tasks)

**Note:** Categories and the category list are shared across all users.

## Default Token Behavior

The default token (`MCP_AUTH_TOKEN`) maps to the default user (`MCP_USER`):

```bash
# In .env.mcp
MCP_AUTH_TOKEN=mcp-secret-token-change-me-in-production  # Maps to admin
MCP_USER=admin
```

So you can still use the default setup for single-user scenarios.

## Example Configuration

Here's a complete example `.env.mcp`:

```bash
# Server settings
MCP_HOST=0.0.0.0
MCP_PORT=8080

# Default token and user (for backward compatibility)
MCP_AUTH_TOKEN=default-secret-token-12345
MCP_USER=admin

# Multi-user mapping
MCP_TOKEN_USER_MAPPING=alice-token-abc123:alice,bob-token-xyz789:bob,charlie-token-def456:charlie

# Django settings
DJANGO_SETTINGS_MODULE=todo_project.settings
```

## Security Best Practices

1. **Use Strong Tokens**
   ```bash
   # Generate with:
   openssl rand -hex 32
   ```

2. **Never Share Tokens**
   - Each user should have their own unique token
   - Don't commit tokens to version control
   - Use environment variables or secrets management in production

3. **HTTPS in Production**
   - Always use HTTPS when deploying
   - Tokens are sent in headers and must be encrypted in transit

4. **Rotate Tokens Regularly**
   - Change tokens periodically
   - Revoke tokens for users who no longer need access

5. **Monitor Access**
   - Check server logs for unusual activity
   - Implement additional rate limiting per user if needed

## Managing Users

### Add a New User

```python
# In Django shell
from django.contrib.auth.models import User
new_user = User.objects.create_user('newuser', 'email@example.com', 'password')
```

Then generate a token and add to `.env.mcp`:
```bash
MCP_TOKEN_USER_MAPPING=existing-tokens,new-token-xyz:newuser
```

Restart the server.

### Remove a User's Access

Remove their token from `MCP_TOKEN_USER_MAPPING` and restart the server.

### List All Users

```bash
python manage.py shell -c "from django.contrib.auth.models import User; [print(u.username) for u in User.objects.all()]"
```

## Integration Examples

### Python Client (Per-User)

```python
class MCPClient:
    def __init__(self, token, base_url="http://localhost:8080"):
        self.token = token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def call_tool(self, tool_name, arguments):
        response = requests.post(
            f"{self.base_url}/messages",
            headers=self.headers,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
        )
        return response.json()

# Usage
alice_client = MCPClient("alice-token-abc123")
bob_client = MCPClient("bob-token-xyz789")

# Alice sees only her tasks
alice_tasks = alice_client.call_tool("list_tasks", {"limit": 10})

# Bob sees only his tasks
bob_tasks = bob_client.call_tool("list_tasks", {"limit": 10})
```

### JavaScript/Node.js Client

```javascript
class MCPClient {
  constructor(token, baseURL = 'http://localhost:8080') {
    this.token = token;
    this.baseURL = baseURL;
  }

  async callTool(toolName, arguments) {
    const response = await fetch(`${this.baseURL}/messages`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: 1,
        method: 'tools/call',
        params: {
          name: toolName,
          arguments: arguments
        }
      })
    });
    return await response.json();
  }
}

// Usage
const aliceClient = new MCPClient('alice-token-abc123');
const bobClient = new MCPClient('bob-token-xyz789');

// Each user gets their own data
const aliceTasks = await aliceClient.callTool('list_tasks', {limit: 10});
const bobTasks = await bobClient.callTool('list_tasks', {limit: 10});
```

## Troubleshooting

### "Unauthorized" errors

- Verify token is in the mapping: `grep "alice-token" .env.mcp`
- Check token format (no spaces, correct separator)
- Restart server after changing `.env.mcp`

### User not found

- Verify user exists: `python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(username='alice').exists())"`
- Check spelling in `MCP_TOKEN_USER_MAPPING`

### Seeing other users' tasks

- Verify you're using the correct token for your user
- Check server logs to see which user is authenticated
- Ensure token mapping is correct in `.env.mcp`

## Comparison: Single-User vs Multi-User

| Feature | Single-User Mode | Multi-User Mode |
|---------|-----------------|-----------------|
| **Configuration** | `MCP_AUTH_TOKEN` + `MCP_USER` | Add `MCP_TOKEN_USER_MAPPING` |
| **Authentication** | One token for default user | Each token maps to specific user |
| **Data Isolation** | All data belongs to default user | Each user sees only their own data |
| **Use Case** | Personal use, single person | Teams, multiple users, SaaS |
| **Setup Complexity** | Simple | Requires user management |

## Summary

✅ **HTTP MCP server now supports multiple users!**

- Each token authenticates as a specific user
- Complete data isolation between users
- Easy to configure with `MCP_TOKEN_USER_MAPPING`
- Backward compatible with single-user setup
- Ready for team deployments and SaaS applications

Now each person can have their own todo list while sharing the same MCP server instance! 🎉
