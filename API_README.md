# Django Todo App - REST API Documentation

## Overview

The Django Todo App now includes a complete REST API built with Django REST Framework. This API allows external clients, mobile apps, web frontends, and integrations to interact with your todo app over HTTP.

## Base URL

```
http://localhost:8000/api/v1/
```

## Authentication

The API uses **Token Authentication**. Include your token in the `Authorization` header:

```
Authorization: Token <your-token>
```

### Getting Your Token

**Option 1: Use existing admin token**
```
Token: 2f60485812cdc76656cd477cf1381be4d0f45717
Username: admin
```

**Option 2: Generate token via API**
```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Response:
```json
{
  "token": "2f60485812cdc76656cd477cf1381be4d0f45717"
}
```

## API Endpoints

### Tasks

#### List Tasks
```bash
GET /api/v1/tasks/

# With filters
GET /api/v1/tasks/?status=todo&priority=3
GET /api/v1/tasks/?category=Work&due_date_gte=2025-11-15
```

**Query Parameters:**
- `status` - Filter by status (todo, in_progress, completed, archived)
- `priority` - Filter by priority (1, 2, 3, 4)
- `category` - Filter by category name
- `due_date_gte` - Tasks due on or after date
- `due_date_lte` - Tasks due on or before date
- `tags_contains` - Filter by tag text
- `search` - Search in title, description, tags
- `ordering` - Sort by field (e.g., `-priority,due_date`)
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20)

#### Create Task
```bash
curl -X POST http://localhost:8000/api/v1/tasks/ \
  -H "Authorization: Token 2f60485812cdc76656cd477cf1381be4d0f45717" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement API endpoints",
    "description": "Build REST API for todo app",
    "category_name": "Development",
    "priority": 3,
    "effort_points": 8,
    "status": "todo",
    "due_date": "2025-11-20",
    "tags": "api, backend"
  }'
```

#### Get Task
```bash
GET /api/v1/tasks/{id}/
```

#### Update Task
```bash
# Full update (PUT)
PUT /api/v1/tasks/{id}/

# Partial update (PATCH)
PATCH /api/v1/tasks/{id}/
  -d '{"status": "in_progress"}'
```

#### Delete Task
```bash
DELETE /api/v1/tasks/{id}/
```

#### Complete Task
```bash
POST /api/v1/tasks/{id}/complete/
```

Response:
```json
{
  "message": "Task 'Implement API endpoints' completed! Earned 8 effort points.",
  "task_id": 11,
  "effort_points": 8
}
```

#### Search Tasks
```bash
GET /api/v1/tasks/search/?q=api
```

### Categories

#### List Categories
```bash
GET /api/v1/categories/
```

#### Create Category
```bash
curl -X POST http://localhost:8000/api/v1/categories/ \
  -H "Authorization: Token 2f60485812cdc76656cd477cf1381be4d0f45717" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Development",
    "description": "Software development tasks",
    "color": "#3498db"
  }'
```

#### Get Category
```bash
GET /api/v1/categories/{id}/
```

#### Get Tasks in Category
```bash
GET /api/v1/categories/{id}/tasks/
```

#### Update Category
```bash
PUT /api/v1/categories/{id}/
PATCH /api/v1/categories/{id}/
```

#### Delete Category
```bash
DELETE /api/v1/categories/{id}/
```

### Notes

#### List Notes
```bash
GET /api/v1/notes/
```

#### Add Note to Task
```bash
curl -X POST http://localhost:8000/api/v1/notes/ \
  -H "Authorization: Token 2f60485812cdc76656cd477cf1381be4d0f45717" \
  -H "Content-Type: application/json" \
  -d '{
    "task": 1,
    "content": "Remember to add unit tests"
  }'
```

#### Get Note
```bash
GET /api/v1/notes/{id}/
```

#### Update Note
```bash
PUT /api/v1/notes/{id}/
PATCH /api/v1/notes/{id}/
```

#### Delete Note
```bash
DELETE /api/v1/notes/{id}/
```

### Analytics

#### Dashboard
```bash
GET /api/v1/analytics/dashboard/
```

Response:
```json
{
  "effort_points": {
    "today": 8,
    "this_week": 25,
    "this_month": 120,
    "this_year": 450
  },
  "task_counts": {
    "todo": 6,
    "in_progress": 2,
    "completed_today": 1
  },
  "upcoming_tasks": [...],
  "overdue_tasks": [...]
}
```

#### Effort Points
```bash
GET /api/v1/analytics/effort-points/
GET /api/v1/analytics/effort-points/?period=week
GET /api/v1/analytics/effort-points/?period=month
```

**Periods:** `today`, `week`, `month`, `year`, `all`

#### Category Breakdown
```bash
GET /api/v1/analytics/category-breakdown/
```

Response:
```json
[
  {
    "task__category__name": "Work",
    "total_points": 85,
    "task_count": 12
  },
  {
    "task__category__name": "Personal",
    "total_points": 45,
    "task_count": 8
  }
]
```

#### Completion History
```bash
GET /api/v1/analytics/completion-history/
GET /api/v1/analytics/completion-history/?limit=20
```

## API Documentation

### Interactive Documentation

Once the server is running, visit:

**Swagger UI** (interactive testing):
```
http://localhost:8000/api/v1/docs/
```

**ReDoc** (beautiful docs):
```
http://localhost:8000/api/v1/redoc/
```

**OpenAPI Schema** (JSON):
```
http://localhost:8000/api/v1/schema/
```

## Example Usage Scenarios

### Scenario 1: Create and Complete a Task

```bash
# 1. Create task
curl -X POST http://localhost:8000/api/v1/tasks/ \
  -H "Authorization: Token 2f60485812cdc76656cd477cf1381be4d0f45717" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Write API documentation",
    "priority": 3,
    "effort_points": 5,
    "category_name": "Documentation"
  }'

# Response: {"id": 15, ...}

# 2. Mark as in progress
curl -X PATCH http://localhost:8000/api/v1/tasks/15/ \
  -H "Authorization: Token 2f60485812cdc76656cd477cf1381be4d0f45717" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'

# 3. Complete the task
curl -X POST http://localhost:8000/api/v1/tasks/15/complete/ \
  -H "Authorization: Token 2f60485812cdc76656cd477cf1381be4d0f45717"

# 4. Check today's points
curl http://localhost:8000/api/v1/analytics/effort-points/?period=today \
  -H "Authorization: Token 2f60485812cdc76656cd477cf1381be4d0f45717"
```

### Scenario 2: Filter High Priority Work Tasks

```bash
curl "http://localhost:8000/api/v1/tasks/?status=todo&priority=4&category=Work&ordering=-due_date" \
  -H "Authorization: Token 2f60485812cdc76656cd477cf1381be4d0f45717"
```

### Scenario 3: Get Productivity Dashboard

```bash
curl http://localhost:8000/api/v1/analytics/dashboard/ \
  -H "Authorization: Token 2f60485812cdc76656cd477cf1381be4d0f45717" | jq
```

## Rate Limiting

- **Anonymous requests**: 100 per day
- **Authenticated requests**: 1000 per day

## Error Responses

### 400 Bad Request
```json
{
  "effort_points": ["Effort points must be between 1 and 10"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

## Response Formats

### Task Object
```json
{
  "id": 1,
  "title": "Task title",
  "description": "Task description",
  "category": {
    "id": 1,
    "name": "Work",
    "color": "#3498db"
  },
  "status": "todo",
  "status_display": "To Do",
  "priority": 3,
  "priority_display": "High",
  "effort_points": 5,
  "due_date": "2025-11-20",
  "tags": "api, backend",
  "user": "admin",
  "created_at": "2025-11-11T15:30:00Z",
  "updated_at": "2025-11-11T15:30:00Z",
  "completed_at": null,
  "llm_suggested": false,
  "llm_automatable": false,
  "llm_metadata": null,
  "notes": []
}
```

### Paginated Response
```json
{
  "count": 45,
  "next": "http://localhost:8000/api/v1/tasks/?page=2",
  "previous": null,
  "results": [...]
}
```

## Integration Examples

### Python (requests)
```python
import requests

TOKEN = "2f60485812cdc76656cd477cf1381be4d0f45717"
BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"Authorization": f"Token {TOKEN}"}

# List tasks
response = requests.get(f"{BASE_URL}/tasks/", headers=HEADERS)
tasks = response.json()

# Create task
data = {
    "title": "New task from Python",
    "priority": 2,
    "effort_points": 3
}
response = requests.post(f"{BASE_URL}/tasks/", json=data, headers=HEADERS)
new_task = response.json()

# Get analytics
response = requests.get(f"{BASE_URL}/analytics/dashboard/", headers=HEADERS)
dashboard = response.json()
print(f"Points today: {dashboard['effort_points']['today']}")
```

### JavaScript (fetch)
```javascript
const TOKEN = "2f60485812cdc76656cd477cf1381be4d0f45717";
const BASE_URL = "http://localhost:8000/api/v1";

// List tasks
fetch(`${BASE_URL}/tasks/`, {
  headers: {
    "Authorization": `Token ${TOKEN}`
  }
})
.then(res => res.json())
.then(data => console.log(data));

// Create task
fetch(`${BASE_URL}/tasks/`, {
  method: "POST",
  headers: {
    "Authorization": `Token ${TOKEN}`,
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    title: "New task from JavaScript",
    priority: 2,
    effort_points: 3
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

### cURL with JQ (bash)
```bash
#!/bin/bash
TOKEN="2f60485812cdc76656cd477cf1381be4d0f45717"
BASE_URL="http://localhost:8000/api/v1"

# Get today's stats
curl -s "${BASE_URL}/analytics/effort-points/?period=today" \
  -H "Authorization: Token ${TOKEN}" | jq

# List urgent tasks
curl -s "${BASE_URL}/tasks/?priority=4&status=todo" \
  -H "Authorization: Token ${TOKEN}" | jq '.results[] | {id, title, due_date}'
```

## Security Notes

1. **HTTPS**: Use HTTPS in production
2. **Token Security**: Keep tokens secret, don't commit to git
3. **CORS**: Configure CORS if accessing from web frontend
4. **Environment Variables**: Store secrets in environment variables

## Coexistence with Other Interfaces

The REST API works alongside:
- **Web UI**: http://localhost:8000/
- **Django Admin**: http://localhost:8000/admin/
- **MCP Server**: stdio (Claude Desktop)

All three access the same database, so changes in one appear immediately in others.

## Troubleshooting

### Token not working
```bash
# Regenerate token
python manage.py shell -c "from rest_framework.authtoken.models import Token; from django.contrib.auth.models import User; user = User.objects.get(username='admin'); Token.objects.filter(user=user).delete(); token = Token.objects.create(user=user); print(token.key)"
```

### 404 errors
Check that the server is running and URL is correct:
```bash
python manage.py runserver
```

### Permission denied
Ensure you're using the correct token and the task/resource belongs to your user.

## Next Steps

1. Start the Django server: `python manage.py runserver`
2. Visit the API docs: http://localhost:8000/api/v1/docs/
3. Try the interactive API testing in Swagger UI
4. Integrate with your favorite client or framework

Enjoy your new REST API!
