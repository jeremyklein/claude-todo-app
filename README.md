# Todo App - Django Task Management System

A comprehensive Django-based todo application for tracking tasks, categorizing them, and monitoring effort points achieved over time.

## Features

### Core Functionality
- **Task Management**: Create, update, delete, and track tasks with multiple statuses (To Do, In Progress, Completed, Archived)
- **Categories**: Organize tasks into color-coded categories
- **Priority Levels**: Four priority levels (Low, Medium, High, Urgent) with visual indicators
- **Effort Points**: Assign effort points (1-10) to tasks to track workload
- **Due Dates**: Set and track task deadlines
- **Tags**: Add comma-separated tags for better organization
- **Notes**: Add detailed notes to any task

### Analytics & Tracking
- **Dashboard**: Real-time overview of tasks and effort points
- **Effort Point Tracking**: Track completed effort points by:
  - Day
  - Week
  - Month
  - Year
- **Visual Analytics**: Charts and graphs showing productivity over time
- **Category Statistics**: See completion rates and effort distribution by category
- **Overdue Task Alerts**: Automatic highlighting of overdue tasks

### Claude Integration via MCP
- **MCP Server**: Connect Claude to your todo app for natural language task management
- **AI Task Management**: Create, update, and complete tasks through conversation with Claude
- **Voice Analytics**: Ask Claude about your productivity and get instant insights
- **Smart Queries**: "Show me my urgent work tasks" or "How many points did I earn this week?"

### REST API (NEW!)
- **Complete HTTP API**: Full REST API with Django REST Framework
- **Token Authentication**: Secure public access with token-based auth
- **24 Endpoints**: Tasks, categories, notes, and analytics
- **Auto Documentation**: Interactive Swagger UI and ReDoc
- **Advanced Features**: Filtering, search, pagination, rate limiting
- **Multi-Client Support**: Mobile apps, web frontends, integrations
- See **API_QUICKSTART.md** for setup and **API_README.md** for full documentation

### Future-Ready Features
- **LLM Integration Fields**: Pre-built fields for future AI integration:
  - `llm_suggested`: Mark AI-suggested tasks
  - `llm_automatable`: Flag tasks that can be automated
  - `llm_metadata`: JSON field for storing AI-related data

## Installation & Setup

### 1. Virtual Environment
The virtual environment is already set up in the `venv` directory.

To activate it:
```bash
source venv/bin/activate
```

### 2. Database
The database is already set up and migrated. Sample data has been loaded.

### 3. Admin Account
A superuser has been created with the following credentials:
- **Username**: admin
- **Password**: admin123

## Running the Application

1. Activate the virtual environment:
```bash
source venv/bin/activate
```

2. Start the development server:
```bash
python manage.py runserver
```

3. Access the application:
- **Main App**: http://127.0.0.1:8000/
- **Admin Interface**: http://127.0.0.1:8000/admin/

## Using the Application

### Dashboard
The main dashboard shows:
- Effort points earned (today, this week, this month, this year)
- Overdue tasks (if any)
- Upcoming tasks (due in next 7 days)
- Tasks in progress
- Top priority to-do tasks
- Tasks completed today
- Category overview with completion rates

### Task Management
- **Create Task**: Click "New Task" in the navigation
- **View Tasks**: Navigate to "Tasks" to see all tasks with filtering options
- **Edit Task**: Click on any task and select "Edit"
- **Complete Task**: Click "Complete" button on any task
- **Add Notes**: Add notes to tasks from the task detail page

### Filtering & Search
Filter tasks by:
- Status (To Do, In Progress, Completed, Archived)
- Category
- Priority
- Search by title, description, or tags

### Analytics
View detailed analytics including:
- Daily points for the last 30 days
- Weekly points for the last 12 weeks
- Monthly points for the last 12 months
- Points breakdown by category
- Recent completions

## Admin Interface

The Django admin interface provides advanced management:
- Bulk actions (mark tasks as completed, in progress, etc.)
- Color-coded priority badges
- Category management with color pickers
- Task completion tracking
- Advanced filtering and search

Access at: http://127.0.0.1:8000/admin/

## Claude Integration (MCP)

Connect your todo app to Claude for natural language task management!

### MCP Servers Available

Your todo app now has **two MCP servers**:

1. **stdio MCP Server** (`mcp_server.py`)
   - For Claude Desktop (local access)
   - No authentication required
   - See **MCP_QUICKSTART.md** for setup

2. **HTTP MCP Server** (`mcp_server_http.py`) ⭐ NEW!
   - For remote access (web, mobile, Claude API)
   - Bearer token authentication
   - **Multi-user support** - each token maps to a specific user
   - Available on http://0.0.0.0:8080
   - See **MCP_HTTP_SETUP.md** for setup
   - See **MULTI_USER_SETUP.md** for multi-user configuration

### Quick Setup (stdio - Claude Desktop)

1. **Add configuration to Claude Desktop**:
   Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

2. **Copy the configuration** from `claude_desktop_config.json` in this directory

3. **Restart Claude Desktop**

4. **Start chatting**: "Show me my todo dashboard" or "Create a high priority task to review the code"

See **MCP_QUICKSTART.md** for 5-minute setup or **MCP_SETUP.md** for detailed documentation.

### Quick Start (HTTP - Remote Access)

1. **Start the HTTP MCP server**:
   ```bash
   source venv-mcp/bin/activate
   python mcp_server_http.py
   ```

2. **Configure authentication** in `.env.mcp`

3. **Access from anywhere**:
   - Claude API
   - Web applications
   - Mobile apps
   - Any HTTP client

See **MCP_HTTP_SETUP.md** for complete documentation and examples.

### What You Can Do with Claude

- Create tasks by describing them naturally
- Check your effort points and analytics
- List and filter tasks by any criteria
- Complete tasks and track progress
- Get productivity insights
- Manage categories and notes

Example: *"Create a task to finish the presentation with 8 effort points in the Work category, make it high priority and due tomorrow"*

## Project Structure

```
todo-app/
├── manage.py
├── mcp_server.py         # MCP server for Claude integration
├── test_mcp.py           # MCP test suite
├── create_sample_data.py # Sample data generator
├── todo_project/         # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── tasks/                # Main app
│   ├── models.py        # Database models
│   ├── views.py         # View logic
│   ├── urls.py          # URL routing
│   ├── admin.py         # Admin configuration
│   └── templates/       # HTML templates
│       ├── base.html
│       ├── tasks/
│       └── registration/
├── static/              # Static files
│   └── css/
│       └── style.css
├── venv/                # Django virtual environment (Python 3.9)
├── venv-mcp/            # MCP virtual environment (Python 3.12)
├── db.sqlite3           # SQLite database
├── README.md            # This file
├── MCP_QUICKSTART.md    # Quick MCP setup guide
├── MCP_SETUP.md         # Detailed MCP documentation
└── claude_desktop_config.json  # Example Claude Desktop config
```

## Database Models

### Category
- Name, description, color
- Tracks all tasks in the category

### Task
- Title, description, status, priority
- Effort points, due date, tags
- Created/updated/completed timestamps
- User association
- LLM integration fields

### TaskCompletion
- Tracks when tasks are completed
- Records effort points at completion
- Provides methods for time-based queries

### Note
- Attached to tasks
- User-created notes with timestamps

## Future LLM Integration

The app is designed with future AI integration in mind:

### Planned Features
1. **Task Creation**: LLM can suggest and create tasks based on user goals
2. **Task Prioritization**: AI-powered priority recommendations
3. **Task Automation**: Identify and automate routine tasks
4. **Smart Scheduling**: AI-suggested due dates based on workload
5. **Progress Insights**: Natural language summaries of productivity

### Integration Points
- Use `llm_suggested` flag to identify AI-created tasks
- Set `llm_automatable` for tasks that can be automated
- Store AI metadata in `llm_metadata` JSON field
- Extend views to handle LLM API calls
- Add LLM configuration in settings

## Customization

### Adding Categories
1. Go to Admin > Categories
2. Click "Add Category"
3. Set name, description, and color (hex code)

### Adjusting Effort Points Scale
Edit `tasks/models.py`:
```python
effort_points = models.IntegerField(default=1, help_text='Estimated effort points (1-10)')
```

### Changing Time Zone
Edit `todo_project/settings.py`:
```python
TIME_ZONE = 'America/New_York'  # Change to your timezone
```

## Development

### Running Migrations
After model changes:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Creating Additional Users
```bash
python manage.py createsuperuser
```

### Running Tests
```bash
python manage.py test
```

## Dependencies

- Django 4.2.26
- Python 3.x
- SQLite (default database)

All dependencies are already installed in the virtual environment.

## Next Steps

1. Start the development server and explore the interface
2. Create your own tasks and categories
3. Complete some tasks to see effort points tracking in action
4. Check out the analytics page to see productivity visualizations
5. Explore the admin interface for advanced management

## Tips

- Use different categories for different areas of life (work, personal, health, etc.)
- Assign effort points consistently (e.g., 1 = quick task, 10 = major project)
- Set realistic due dates to avoid overwhelm
- Review the analytics regularly to understand your productivity patterns
- Use tags for flexible organization beyond categories

## Future Enhancements

Potential additions:
- REST API for mobile app integration
- Task templates
- Recurring tasks
- Team collaboration features
- Calendar integration
- Email notifications
- Export functionality (CSV, PDF)
- Dark mode toggle
- Custom themes

Enjoy tracking your productivity!
