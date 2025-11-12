# REST API Quick Start Guide

## What's Been Added

Your Django Todo App now has a **complete REST API** that allows web/HTTP access alongside the existing MCP server and web interface.

## 5-Minute Quick Start

### 1. Start the Server

```bash
cd /Users/jeremyklein/development/todo-app
source venv/bin/activate
python manage.py runserver
```

### 2. Test the API

In another terminal:

```bash
cd /Users/jeremyklein/development/todo-app
./test_api.sh
```

You should see all tests pass ✓

### 3. View Interactive Documentation

Open your browser:
- **Swagger UI**: http://localhost:8000/api/v1/docs/
- **ReDoc**: http://localhost:8000/api/v1/redoc/

### 4. Try Your First API Call

```bash
# Your API token (already created)
TOKEN="2f60485812cdc76656cd477cf1381be4d0f45717"

# List all tasks
curl http://localhost:8000/api/v1/tasks/ \
  -H "Authorization: Token ${TOKEN}"

# Create a task
curl -X POST http://localhost:8000/api/v1/tasks/ \
  -H "Authorization: Token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My first API task",
    "priority": 2,
    "effort_points": 3
  }'

# Get today's effort points
curl http://localhost:8000/api/v1/analytics/dashboard/ \
  -H "Authorization: Token ${TOKEN}"
```

## What's Available

### Endpoints Summary

**Tasks** (9 endpoints)
- `GET /api/v1/tasks/` - List tasks with filters
- `POST /api/v1/tasks/` - Create task
- `GET /api/v1/tasks/{id}/` - Get task
- `PATCH /api/v1/tasks/{id}/` - Update task
- `DELETE /api/v1/tasks/{id}/` - Delete task
- `POST /api/v1/tasks/{id}/complete/` - Mark complete
- `GET /api/v1/tasks/search/?q=query` - Search tasks

**Categories** (6 endpoints)
- Full CRUD + list tasks in category

**Notes** (5 endpoints)
- Full CRUD for task notes

**Analytics** (4 endpoints)
- Dashboard overview
- Effort points by period
- Category breakdown
- Completion history

**Documentation**
- Swagger UI at `/api/v1/docs/`
- ReDoc at `/api/v1/redoc/`
- OpenAPI schema at `/api/v1/schema/`

## Key Features

✅ **Token Authentication** - Secure public access
✅ **Advanced Filtering** - Filter by status, priority, category, dates
✅ **Full Text Search** - Search in title, description, tags
✅ **Pagination** - 20 items per page (configurable)
✅ **Rate Limiting** - 1000 requests/day per user
✅ **Auto Documentation** - Interactive Swagger UI
✅ **User Isolation** - Users can only access their own tasks

## Integration Examples

### Python
```python
import requests

TOKEN = "2f60485812cdc76656cd477cf1381be4d0f45717"
BASE_URL = "http://localhost:8000/api/v1"

# Get dashboard
response = requests.get(
    f"{BASE_URL}/analytics/dashboard/",
    headers={"Authorization": f"Token {TOKEN}"}
)
print(response.json())
```

### JavaScript
```javascript
const response = await fetch('http://localhost:8000/api/v1/tasks/', {
  headers: {
    'Authorization': 'Token 2f60485812cdc76656cd477cf1381be4d0f45717'
  }
});
const tasks = await response.json();
```

### cURL
```bash
curl http://localhost:8000/api/v1/tasks/?status=todo&priority=3 \
  -H "Authorization: Token 2f60485812cdc76656cd477cf1381be4d0f45717"
```

## Three Ways to Access Your Todo App

1. **MCP Server** (stdio) → Claude Desktop
2. **Web UI** (HTML) → http://localhost:8000/
3. **REST API** (JSON) → http://localhost:8000/api/v1/ ⭐ NEW

All three share the same database!

## Documentation

- **Full API Docs**: See `API_README.md`
- **Interactive Testing**: http://localhost:8000/api/v1/docs/
- **Test Script**: `./test_api.sh`

## Common Use Cases

### Mobile App
Use the API to build iOS/Android apps that sync with your todo data.

### Web Frontend
Build a React/Vue/Angular frontend that consumes the API.

### Integrations
Connect to Zapier, IFTTT, or custom scripts to automate task management.

### External Services
Let other services create tasks via webhooks or API calls.

## Security

- **Token-based auth**: Each request requires a valid token
- **User isolation**: Users can only access their own data
- **Rate limiting**: Prevents API abuse
- **HTTPS ready**: Configure for production use

## Next Steps

1. ✅ API is already set up and working
2. ✅ Test it with `./test_api.sh`
3. 📖 Read `API_README.md` for detailed documentation
4. 🔧 Integrate with your favorite client/framework
5. 🚀 Deploy to production with HTTPS

Enjoy your new REST API!
