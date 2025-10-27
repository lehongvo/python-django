# 🐳 Django Blog - Docker Setup Guide

## Prerequisites

- Docker Desktop installed and running
- Git installed (optional)

## Quick Start

### Method 1: Using Scripts (Recommended)

**For macOS/Linux:**
```bash
cd Day1/Exercise
bash start.sh
```

**For Windows:**
```bash
cd Day1/Exercise
start.bat
```

### Method 2: Manual Setup

```bash
# Navigate to Exercise directory
cd Day1/Exercise

# Build and start Docker containers
docker-compose up --build

# In another terminal, create superuser
docker-compose exec web python manage.py createsuperuser
# Enter username: admin
# Enter email: admin@example.com
# Enter password: admin123
```

## Accessing the Application

Once Docker containers are running:

- **Blog**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin

### Default Admin Credentials

After running the setup script:
- **Username**: admin
- **Password**: admin123

**Important**: Change the password after first login!

## Common Commands

### Start the application
```bash
docker-compose up -d
```

### Stop the application
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f
```

### Access Django shell
```bash
docker-compose exec web python manage.py shell
```

### Run migrations
```bash
docker-compose exec web python manage.py migrate
```

### Create superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

### View running containers
```bash
docker-compose ps
```

### Restart containers
```bash
docker-compose restart
```

### Rebuild containers (after code changes)
```bash
docker-compose up --build
```

## Project Structure

```
Day1/Exercise/
├── blogproject/          # Django project configuration
│   ├── settings.py       # Django settings
│   ├── urls.py          # Main URL routing
│   └── ...
├── blog/                 # Blog app
│   ├── models.py        # Database models
│   ├── views.py         # View functions
│   ├── urls.py          # App URL routing
│   ├── admin.py         # Admin configuration
│   └── templates/       # HTML templates
│       ├── base.html
│       └── blog/
├── blog/templates/       # HTML templates
│   ├── base.html
│   └── blog/
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── requirements.txt      # Python dependencies
└── start.sh / start.bat  # Startup scripts
```

## Features

✅ Full CRUD Operations
- **Create**: Add new blog posts
- **Read**: View posts list and details
- **Update**: Edit existing posts
- **Delete**: Remove posts

✅ Additional Features
- Beautiful gradient UI
- Responsive design
- Admin interface
- Django admin panel
- Success/error messages
- Post publish/draft status

## Troubleshooting

### Docker daemon not running

**Error**: `Cannot connect to the Docker daemon`

**Solution**: Start Docker Desktop application

### Port 8000 already in use

**Error**: `Port 8000 is already allocated`

**Solution**: 
```bash
# Option 1: Stop other services using port 8000
lsof -ti:8000 | xargs kill

# Option 2: Change port in docker-compose.yml
# Change "8000:8000" to "8001:8000"
# Then access at http://localhost:8001
```

### Containers won't start

**Solution**: Check logs
```bash
docker-compose logs
```

### Database errors

**Solution**: Reset database
```bash
docker-compose down
docker-compose exec web python manage.py flush
docker-compose exec web python manage.py migrate
```

### Cannot access admin

**Solution**: Create superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

## Development Mode

To work on the code:

1. Containers are running
2. Edit files on your machine
3. Changes reflect immediately (volume mounted)
4. Refresh browser to see changes

## Production Considerations

⚠️ **This setup is for DEVELOPMENT only!**

For production:
- Change `DEBUG = False`
- Use environment variables for SECRET_KEY
- Set up proper database (PostgreSQL)
- Use production-ready web server (gunicorn)
- Configure nginx
- Set up SSL/TLS
- Add proper logging

## Files Created by Docker

These files will be created when you run Docker:
- `db.sqlite3` - SQLite database
- `__pycache__/` - Python cache files
- `*.pyc` - Compiled Python files

They are already in `.gitignore`.

## Next Steps

1. ✅ Project is running
2. Visit http://localhost:8000
3. Click "New Post" to create your first post
4. Explore the admin panel
5. Try all CRUD operations
6. Read the code to understand Django
7. Experiment and learn!

## Need Help?

- Check Django documentation: https://docs.djangoproject.com/
- Review the `instructions.md` file
- Look at the `solution/` folder for reference
- Read the `Learn/` materials

---

**Happy Coding!** 🚀

