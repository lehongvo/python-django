# Django Quick Reference Notes

## Key Concepts

### Projects vs Apps
- **Project**: Collection of apps and configuration
- **App**: Self-contained module for specific functionality
- One project → Multiple apps
- Apps can be reused

### MVT Pattern
- **Model**: Data and database
- **View**: Business logic
- **Template**: HTML presentation

## File Structure

```
myproject/
├── manage.py              # Management commands
├── db.sqlite3             # Database
├── requirements.txt        # Dependencies
├── myproject/             # Project config
│   ├── settings.py        # Configuration
│   ├── urls.py            # URL routing
│   ├── wsgi.py            # WSGI config
│   └── asgi.py            # ASGI config
└── myapp/                 # Django app
    ├── models.py          # Data models
    ├── views.py           # View logic
    ├── urls.py            # App URLs
    ├── admin.py           # Admin config
    └── migrations/        # DB migrations
```

## Essential Commands

```bash
# Create project
django-admin startproject myproject .

# Create app
python manage.py startapp myapp

# Run server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell
```

## URL Configuration

### Project URLs
```python
# myproject/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('app/', include('myapp.urls')),
]
```

### App URLs
```python
# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<int:id>/', views.detail, name='detail'),
]
```

## Models

```python
# models.py
from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
```

## Views

### Function-Based Views
```python
from django.shortcuts import render, get_object_or_404
from .models import Post

def index(request):
    posts = Post.objects.all()
    return render(request, 'app/index.html', {'posts': posts})

def detail(request, id):
    post = get_object_or_404(Post, id=id)
    return render(request, 'app/detail.html', {'post': post})
```

### Class-Based Views
```python
from django.views.generic import ListView, DetailView
from .models import Post

class PostListView(ListView):
    model = Post
    template_name = 'app/list.html'

class PostDetailView(DetailView):
    model = Post
    template_name = 'app/detail.html'
```

## Templates

### Base Template
```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}My Site{% endblock %}</title>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
```

### Template Tags
```html
{# Variables #}
{{ variable }}

{# Tags #}
{% if condition %}
{% for item in items %}
{% endblock %}

{# Filters #}
{{ value|upper }}
{{ date|date:"Y-m-d" }}
```

## Admin

```python
# admin.py
from django.contrib import admin
from .models import Post

admin.site.register(Post)
```

## ORM Queries

```python
# Get all
Post.objects.all()

# Filter
Post.objects.filter(is_published=True)

# Get one
Post.objects.get(id=1)

# Create
Post.objects.create(title="New", content="...")

# Update
post = Post.objects.get(id=1)
post.title = "Updated"
post.save()

# Delete
post = Post.objects.get(id=1)
post.delete()
```

## Form Handling

```python
# views.py
from django.shortcuts import render, redirect
from .forms import PostForm

def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = PostForm()
    return render(request, 'app/form.html', {'form': form})
```

## Common Field Types

- `CharField`: Short text
- `TextField`: Long text
- `IntegerField`: Numbers
- `DateTimeField`: Date/time
- `BooleanField`: True/False
- `ForeignKey`: Related object
- `ManyToManyField`: Multiple relations

## Settings Configuration

```python
# settings.py

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myapp',  # Your app
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

## Security Checklist

- [ ] Set DEBUG = False in production
- [ ] Set ALLOWED_HOSTS
- [ ] Use SECRET_KEY environment variable
- [ ] Use HTTPS
- [ ] Enable CSRF protection
- [ ] Use password hashing
- [ ] Validate user input
- [ ] Protect admin with strong password

## Troubleshooting

**Server won't start**: Check port 8000 is free
**Migrations error**: Delete db.sqlite3 and migrations folder
**Import error**: Check INSTALLED_APPS includes your app
**Template not found**: Check TEMPLATES setting and file paths
**Static files not loading**: Run collectstatic in production

