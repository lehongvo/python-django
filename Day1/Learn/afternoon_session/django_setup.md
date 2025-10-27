# Setting Up Django Development Environment

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- A code editor (VS Code, PyCharm, etc.)
- Virtual environment support

## Step-by-Step Setup

### 1. Check Python Version

```bash
python3 --version
# or
python --version
```

Should be 3.8 or higher. If not, install a newer version.

### 2. Create Project Directory

```bash
mkdir mydjangoproject
cd mydjangoproject
```

### 3. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

### 4. Upgrade pip

```bash
pip install --upgrade pip
```

### 5. Install Django

```bash
# Install latest stable version
pip install django

# Install specific version
pip install django==4.2.0

# Install development version (not recommended for production)
pip install django --pre
```

### 6. Verify Installation

```bash
# Check Django version
python -m django --version

# Or using django-admin
django-admin --version
```

### 7. Create Django Project

```bash
# Create a new Django project
django-admin startproject myproject .

# The dot (.) creates the project in current directory
# Without dot, it creates a subdirectory
```

### 8. Test the Development Server

```bash
# Run the development server
python manage.py runserver

# Access at http://127.0.0.1:8000/
```

### 9. Create a Django App

```bash
# Create your first app
python manage.py startapp myapp
```

### 10. Create requirements.txt

```bash
# Generate requirements file
pip freeze > requirements.txt
```

## Project Structure After Setup

```
mydjangoproject/
├── venv/                      # Virtual environment (not in git)
├── manage.py                  # Django management script
├── db.sqlite3                 # SQLite database (gitignored)
├── requirements.txt           # Dependencies
├── .gitignore                 # Git ignore file
└── myproject/                 # Project configuration
    ├── __init__.py
    ├── settings.py            # Django settings
    ├── urls.py                # URL configuration
    ├── wsgi.py                # WSGI config for deployment
    └── asgi.py                # ASGI config for async
```

## Important Files

### manage.py
Command-line utility for Django operations.

### settings.py
All configuration for your Django project:
- Database settings
- Installed apps
- Middleware
- Timezone, language
- Static files
- Security settings

### urls.py
URL routing configuration.

### wsgi.py / asgi.py
Server entry points for deployment.

## Common Setup Issues

### Issue 1: "django-admin: command not found"
**Solution**: 
- Make sure virtual environment is activated
- Install Django: `pip install django`

### Issue 2: "No module named django"
**Solution**:
- Activate virtual environment: `source venv/bin/activate`
- Verify with: `python -m django --version`

### Issue 3: Port 8000 already in use
**Solution**:
```bash
# Use a different port
python manage.py runserver 8080

# Or stop the process using port 8000
lsof -ti:8000 | xargs kill
```

### Issue 4: Import errors in settings.py
**Solution**:
- Make sure you're in the project directory
- Check that manage.py is in the current directory

## Development Workflow

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Make changes to your code

# 3. Test locally
python manage.py runserver

# 4. Make migrations if you changed models
python manage.py makemigrations

# 5. Apply migrations
python manage.py migrate

# 6. Create superuser (first time)
python manage.py createsuperuser

# 7. Deactivate when done
deactivate
```

## Recommended VS Code Setup

### Install Extensions

```bash
# Recommended extensions:
# - Python
# - Django
# - Python Docstring Generator
# - Django Template
```

### .vscode/settings.json

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "files.associations": {
        "**/*.html": "html",
        "**/templates/**": "django-html"
    }
}
```

## Additional Setup (Optional)

### Install Django Extensions

```bash
pip install django-extensions
pip install ipython
```

Add to INSTALLED_APPS in settings.py:
```python
INSTALLED_APPS = [
    # ... existing apps
    'django_extensions',
]
```

### Install Useful Packages

```bash
pip install python-decouple  # Environment variables
pip install django-crispy-forms  # Form styling
pip install pillow  # Image handling
```

## Next Steps

1. Create your first app: `python manage.py startapp myapp`
2. Configure settings.py
3. Create your first view
4. Set up URL routing
5. Create templates
6. Run migrations

## Quick Reference Commands

```bash
# Activate environment
source venv/bin/activate

# Install Django
pip install django

# Create project
django-admin startproject myproject .

# Create app
python manage.py startapp myapp

# Run server
python manage.py runserver

# Create superuser
python manage.py createsuperuser

# Migrations
python manage.py makemigrations
python manage.py migrate

# Check for issues
python manage.py check

# Start shell
python manage.py shell
```

