# Introduction to Django Framework

## What is Django?

Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design. It follows the "batteries included" philosophy, providing everything needed for web development.

## Key Features

- **Rapid Development**: Built for developers to take ideas from concept to completion quickly
- **Fully Loaded**: Includes admin interface, authentication, and more out-of-the-box
- **Secure**: Helps avoid common security mistakes automatically
- **Scalable**: Used by large companies like Instagram, Spotify, YouTube
- **Versatile**: Can build any type of web application

## Django Philosophy

### DRY (Don't Repeat Yourself)
- Write code once and reuse it everywhere
- Django provides reusable components

### Convention over Configuration
- Sensible defaults
- Less configuration, more convention

### Loose Coupling
- Different parts of the application work independently
- Easy to modify and extend

## Django Architecture

### MVT Pattern (Model-View-Template)

```
┌─────────────────────────────────────┐
│         URL Configuration            │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│              View (Controller)         │
│  - Handles logic                    │
│  - Processes data                   │
│  - Returns responses                │
└─────────────────────────────────────┘
         ↓                    ↓
┌────────────┐      ┌─────────────────┐
│   Model    │      │    Template     │
│ - Database │      │    - HTML       │
│ - Business │      │    - Display    │
│   Logic    │      │                 │
└────────────┘      └─────────────────┘
```

### Components:

1. **Model**: Data structure and database interactions
2. **View**: Business logic and data processing
3. **Template**: HTML presentation layer

## Django Project Structure

```
myproject/
├── manage.py                 # Command-line utility
├── db.sqlite3                # Default database
├── myproject/                # Main project directory
│   ├── __init__.py
│   ├── settings.py           # Settings/configuration
│   ├── urls.py               # URL routing
│   ├── wsgi.py               # WSGI configuration
│   └── asgi.py               # ASGI configuration
└── myapp/                    # Django app
    ├── __init__.py
    ├── admin.py              # Admin configuration
    ├── apps.py               # App configuration
    ├── models.py             # Data models
    ├── views.py              # Views/controllers
    ├── urls.py               # App URL routing
    ├── tests.py              # Unit tests
    └── migrations/           # Database migrations
```

## Key Concepts

### 1. Projects vs Apps

- **Project**: Collection of apps and configuration
- **App**: Self-contained module for specific functionality
- **One project** can have **multiple apps**
- Apps can be reused across projects

### 2. URL Routing

```python
# urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')),
]
```

### 3. Views

```python
# views.py
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, World!")
```

### 4. Models

```python
# models.py
from django.db import models

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
```

### 5. Templates

```html
<!-- template.html -->
<h1>{{ post.title }}</h1>
<p>{{ post.content }}</p>
```

## Django ORM

Object-Relational Mapping allows you to interact with databases using Python classes instead of SQL.

### Benefits

- **Database independent**: Works with PostgreSQL, MySQL, SQLite, etc.
- **Type safe**: Python classes instead of raw SQL
- **Migrations**: Automatic database schema management

### Example

```python
# Instead of SQL
SELECT * FROM blog_posts WHERE published_date > '2023-01-01';

# Django ORM
BlogPost.objects.filter(published_date__gt='2023-01-01')
```

## Django Admin

Built-in administration interface:

- Automatic: Generated from your models
- Customizable: Easy to configure and extend
- Secure: Built-in authentication and permissions

## Security Features

1. **CSRF Protection**: Cross-Site Request Forgery protection
2. **SQL Injection Protection**: ORM prevents SQL injection
3. **XSS Protection**: Template escaping by default
4. **Clickjacking Protection**: X-Frame-Options middleware
5. **Password Hashing**: Secure password storage
6. **Session Security**: Secure session management

## When to Use Django

✅ **Use Django when:**
- Building web applications
- Need database integration
- Want rapid development
- Need admin interface
- Building RESTful APIs (with DRF)

❌ **Consider alternatives when:**
- Building microservices (FastAPI might be better)
- Real-time applications (Flask or FastAPI with WebSockets)
- Simple static sites (not necessary)

## Django Ecosystem

- **Django REST Framework**: Building REST APIs
- **Django Channels**: WebSockets and async support
- **Django Celery**: Task queue management
- **Django Haystack**: Full-text search
- **Django Debug Toolbar**: Development debugging

## Next Steps

1. Install Django
2. Create your first project
3. Learn about the MVT pattern in detail
4. Build a simple application
5. Explore Django admin
6. Deploy your application

## Resources

- **Official Documentation**: https://docs.djangoproject.com/
- **Django Tutorial**: Official 7-part tutorial
- **Django Girls**: Beginner-friendly tutorials
- **Two Scoops of Django**: Best practices book
- **Real Python**: Django tutorials and articles

