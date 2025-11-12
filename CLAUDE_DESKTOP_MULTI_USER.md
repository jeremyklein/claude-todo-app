# Claude Desktop Multi-User Setup

## The Problem

By default, the stdio MCP server uses a single default user (`admin`). If multiple people use Claude Desktop on different machines, they'll all see the same user's tasks.

## The Solution

Configure each Claude Desktop installation to use a different Django user by setting the `MCP_USER` environment variable.

## Prerequisites

### 1. Create Django Users

First, create a Django user for each person:

```bash
cd /Users/jeremyklein/development/todo-app
source venv/bin/activate
python manage.py shell
```

```python
from django.contrib.auth.models import User

# Create users
User.objects.create_user('alice', 'alice@example.com', 'password123')
User.objects.create_user('bob', 'bob@example.com', 'password123')
User.objects.create_user('charlie', 'charlie@example.com', 'password123')

print("Users created!")
```

### 2. Verify Users Exist

```bash
python manage.py shell -c "from django.contrib.auth.models import User; [print(u.username) for u in User.objects.all()]"
```

## Configuration for Each Person

### Alice's Configuration

On Alice's machine, edit:
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

Add:
```json
{
  "mcpServers": {
    "django-todo": {
      "command": "/Users/alice/development/todo-app/venv-mcp/bin/python",
      "args": ["/Users/alice/development/todo-app/mcp_server.py"],
      "env": {
        "MCP_USER": "alice"
      }
    }
  }
}
```

**Important:** Update the paths to match Alice's actual installation location.

### Bob's Configuration

On Bob's machine, edit:
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

Add:
```json
{
  "mcpServers": {
    "django-todo": {
      "command": "/Users/bob/projects/todo-app/venv-mcp/bin/python",
      "args": ["/Users/bob/projects/todo-app/mcp_server.py"],
      "env": {
        "MCP_USER": "bob"
      }
    }
  }
}
```

### Charlie's Configuration

On Charlie's machine:
```json
{
  "mcpServers": {
    "django-todo": {
      "command": "/Users/charlie/code/todo-app/venv-mcp/bin/python",
      "args": ["/Users/charlie/code/todo-app/mcp_server.py"],
      "env": {
        "MCP_USER": "charlie"
      }
    }
  }
}
```

## How It Works

1. **Each person** has their own Claude Desktop installation
2. **Each installation** points to their own copy of the todo app
3. **Each copy** uses a different `MCP_USER` environment variable
4. **Each user** only sees their own tasks

## Important Considerations

### Shared Database vs. Separate Databases

You have two options:

#### Option 1: Separate Databases (Recommended for Most Cases)
- Each person has their own todo app installation
- Each has their own `db.sqlite3` database file
- Complete data isolation
- No shared configuration needed

**Setup:** Each person clones/copies the repo independently.

#### Option 2: Shared Database (For Teams)
- One centralized database server (PostgreSQL/MySQL)
- All users connect to the same database
- Users see only their own tasks (filtered by `user` field)
- Requires network-accessible database

**Setup:**
1. Set up PostgreSQL or MySQL
2. Update `settings.py` to use the shared database:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'todo_db',
           'USER': 'db_user',
           'PASSWORD': 'db_password',
           'HOST': 'database.example.com',
           'PORT': '5432',
       }
   }
   ```
3. Each user's MCP server connects to the same database
4. `MCP_USER` determines which user's tasks they see

## Verification

After configuring, test in Claude Desktop:

**Alice's Claude Desktop:**
```
User: "Show me my tasks"
Claude: [Shows only Alice's tasks]

User: "Create a task to buy groceries"
Claude: [Creates task for Alice]
```

**Bob's Claude Desktop:**
```
User: "Show me my tasks"
Claude: [Shows only Bob's tasks - different from Alice's]

User: "What's on my dashboard?"
Claude: [Shows Bob's dashboard with Bob's stats]
```

## Troubleshooting

### "No user found" error

**Problem:** The username in `MCP_USER` doesn't exist in the database.

**Solution:**
```bash
# Check if user exists
cd /path/to/todo-app
source venv/bin/activate
python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(username='alice').exists())"

# If False, create the user:
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_user('alice', 'alice@example.com', 'password')"
```

### Still seeing other users' tasks

**Problem:** The environment variable isn't being applied.

**Solutions:**
1. Check spelling of username in config
2. Restart Claude Desktop completely (Cmd+Q, then reopen)
3. Verify the config file is valid JSON (check for trailing commas, missing quotes)
4. Check Claude Desktop logs for errors

### Path issues

**Problem:** Claude Desktop can't find the Python executable or script.

**Solution:**
- Use absolute paths (start with `/Users/...`)
- Verify paths exist: `ls /Users/alice/development/todo-app/venv-mcp/bin/python`
- Check permissions: `chmod +x /path/to/mcp_server.py`

## Alternative: Use Django Admin for User Management

You can also use the Django admin interface to manage users:

1. Start the Django dev server:
   ```bash
   cd /path/to/todo-app
   source venv/bin/activate
   python manage.py runserver
   ```

2. Go to http://localhost:8000/admin/

3. Log in with admin credentials

4. Go to "Users" → "Add User"

5. Create a new user with username/password

6. Use that username in `MCP_USER`

## Example: Team Setup with Shared Database

**Scenario:** A team of 3 sharing a PostgreSQL database

**Database Setup:**
```bash
# On database server
createdb todo_team_db
```

**settings.py (same for everyone):**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'todo_team_db',
        'USER': 'todo_user',
        'PASSWORD': 'secure_password',
        'HOST': 'db.company.com',
        'PORT': '5432',
    }
}
```

**Alice's config:**
```json
{
  "mcpServers": {
    "django-todo": {
      "command": "/Users/alice/todo-app/venv-mcp/bin/python",
      "args": ["/Users/alice/todo-app/mcp_server.py"],
      "env": {
        "MCP_USER": "alice"
      }
    }
  }
}
```

**Bob's config:**
```json
{
  "mcpServers": {
    "django-todo": {
      "command": "/Users/bob/todo-app/venv-mcp/bin/python",
      "args": ["/Users/bob/todo-app/mcp_server.py"],
      "env": {
        "MCP_USER": "bob"
      }
    }
  }
}
```

Now Alice and Bob connect to the same database but only see their own tasks!

## Security Considerations

### Local (Separate Databases)
- ✅ Complete isolation - each user has their own database file
- ✅ No network exposure
- ✅ Simple setup
- ❌ No collaboration features

### Shared Database
- ✅ Enables collaboration (shared categories, etc.)
- ⚠️ Requires network security (VPN, firewall)
- ⚠️ Requires proper Django user permissions
- ⚠️ Database credentials must be secured

## Summary

| Aspect | Single-User | Multi-User (Separate DBs) | Multi-User (Shared DB) |
|--------|------------|---------------------------|------------------------|
| **Config** | Default `MCP_USER=admin` | Each: `MCP_USER=username` | Each: `MCP_USER=username` |
| **Database** | One db.sqlite3 | Multiple db.sqlite3 files | One shared PostgreSQL/MySQL |
| **Isolation** | N/A (one user) | Complete (separate DBs) | User field filtering |
| **Setup** | Simple | Simple | Complex (DB server) |
| **Use Case** | Personal | Personal, team (no sharing) | Team with collaboration |

## Quick Reference

**For personal use (most common):**
```json
{
  "mcpServers": {
    "django-todo": {
      "command": "/full/path/to/venv-mcp/bin/python",
      "args": ["/full/path/to/mcp_server.py"],
      "env": {
        "MCP_USER": "your-username"
      }
    }
  }
}
```

**Key points:**
- ✅ Use absolute paths
- ✅ Set `MCP_USER` to your Django username
- ✅ Create the Django user first
- ✅ Restart Claude Desktop after config changes

That's it! Now each person's Claude Desktop connects as their own user. 🎉
