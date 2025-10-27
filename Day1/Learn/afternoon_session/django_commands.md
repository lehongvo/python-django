# Basic Django Commands

This guide covers essential Django commands you'll use throughout development.

## Project Creation Commands

### Create a New Django Project

```bash
# Create project in current directory
django-admin startproject myproject .

# Create project in new subdirectory
django-admin startproject myproject
```

**Files Created**:
- `manage.py`: Django management script
- `myproject/` directory with:
  - `settings.py`: Configuration
  - `urls.py`: URL routing
  - `wsgi.py`: Deployment config
  - `asgi.py`: Async config

### Create a New Django App

```bash
# Create app in your project
python manage.py startapp myapp
```

**Files Created**:
- `myapp/` directory with:
  - `models.py`: Data models
  - `views.py`: View functions
  - `admin.py`: Admin configuration
  - `apps.py`: App configuration
  - `tests.py`: Unit tests
  - `urls.py`: (you create this)
  - `migrations/`: Database migrations

## Development Server Commands

### Run Development Server

```bash
# Start server on default port (8000)
python manage.py runserver

# Start on specific port
python manage.py runserver 8080

# Start on specific IP and port
python manage.py runserver 127.0.0.1:8080

# Make server accessible on network
python manage.py runserver 0.0.0.0:8000
```

**Access**: http://127.0.0.1:8000/

**Features**:
- Auto-reload on code changes
- Debug toolbar
- Error pages
- Development-only, not for production

## Database Commands

### Migrations

```bash
# Create migration files for model changes
python manage.py makemigrations

# Create migrations for specific app
python manage.py makemigrations myapp

# Show SQL for pending migrations
python manage.py sqlmigrate myapp 0001

# Show migration status
python manage.py showmigrations

# Apply migrations
python manage.py migrate

# Apply specific migration
python manage.py migrate myapp 0001

# Rollback migrations
python manage.py migrate myapp previous_migration
```

**Migration Files Location**: `myapp/migrations/0001_initial.py`

### Reset Database

```bash
# Delete database (SQLite)
rm db.sqlite3

# Remove migrations (except __init__.py)
rm myapp/migrations/0*.py

# Recreate migrations and database
python manage.py makemigrations
python manage.py migrate
```

## Admin Commands

### Create Superuser

```bash
# Interactive superuser creation
python manage.py createsuperuser

# Non-interactive (advanced)
python manage.py shell
# Then in shell:
from django.contrib.auth.models import User
User.objects.create_superuser('admin', 'admin@example.com', 'password')
```

**Admin Access**: http://127.0.0.1:8000/admin/

### Register Models in Admin

```python
# myapp/admin.py
from django.contrib import admin
from .models import BlogPost

admin.site.register(BlogPost)
```

## Management Commands

### Django Shell

```bash
# Start Django shell
python manage.py shell

# Start with iPython (if installed)
python manage.py shell_plus

# Import models in shell
from myapp.models import BlogPost
BlogPost.objects.all()
```

### Collect Static Files

```bash
# Collect static files for production
python manage.py collectstatic

# Don't ask for confirmation
python manage.py collectstatic --noinput
```

### Check Project

```bash
# Check for common problems
python manage.py check

# Check specific app
python manage.py check myapp

# Check deployment settings
python manage.py check --deploy
```

### Inspect Database

```bash
# Inspect database schema
python manage.py inspectdb

# Save to models.py
python manage.py inspectdb > myapp/models.py
```

## Useful Development Commands

### Run Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test myapp

# Run specific test class
python manage.py test myapp.tests.TestViews

# Run with verbosity
python manage.py test --verbosity 2

# Keep test database
python manage.py test --keepdb
```

### Clear Cache

```bash
# Start shell
python manage.py shell

# Then in shell:
from django.core.cache import cache
cache.clear()
```

### Show URLs

```bash
# Start shell
python manage.py shell

# Then in shell:
from django.urls import get_resolver
urls = get_resolver().url_patterns
for url in urls:
    print(url)
```

## Complete Workflow Example

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install Django
pip install django

# 3. Create project
django-admin startproject myproject .

# 4. Create app
python manage.py startapp blog

# 5. Define models
# Edit blog/models.py

# 6. Create migrations
python manage.py makemigrations

# 7. Apply migrations
python manage.py migrate

# 8. Create superuser
python manage.py createsuperuser

# 9. Run server
python manage.py runserver

# 10. Visit admin and site
# http://127.0.0.1:8000/admin/
# http://127.0.0.1:8000/
```

## Common Mistakes and Solutions

### Mistake 1: "You have unapplied migrations"
```bash
# Solution: Apply migrations
python manage.py migrate
```

### Mistake 2: "No such table"
```bash
# Solution: Create and apply migrations
python manage.py makemigrations
python manage.py migrate
```

### Mistake 3: "App not in INSTALLED_APPS"
```python
# Solution: Add to settings.py
INSTALLED_APPS = [
    # ...
    'myapp',
]
```

### Mistake 4: "Changes not detected"
```bash
# Solution: Hard reload server
# Press Ctrl+C to stop, then restart
python manage.py runserver
```

## Command Line Shortcuts

```bash
# Alias for runserver
alias dj='python manage.py runserver'

# Alias for shell
alias djshell='python manage.py shell'

# Alias for migrate
alias djmigrate='python manage.py makemigrations && python manage.py migrate'
```

## Cheat Sheet

| Command | Purpose |
|---------|---------|
| `python manage.py runserver` | Start dev server |
| `python manage.py startapp` | Create new app |
| `python manage.py makemigrations` | Create migration files |
| `python manage.py migrate` | Apply migrations |
| `python manage.py createsuperuser` | Create admin user |
| `python manage.py shell` | Interactive shell |
| `python manage.py test` | Run tests |
| `python manage.py check` | Check for issues |

## Next Steps

1. Practice creating projects and apps
2. Run migrations after model changes
3. Create superuser for admin access
4. Use shell to interact with models
5. Run tests regularly

