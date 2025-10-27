# Django Blog Exercise - Step-by-Step Instructions

## Part 1: Project Setup

### Step 1.1: Create Virtual Environment

```bash
# Navigate to Exercise directory
cd Day1/Exercise

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Upgrade pip
pip install --upgrade pip
```

### Step 1.2: Install Django

```bash
# Install Django
pip install django

# Verify installation
python -m django --version

# Create requirements.txt
pip freeze > requirements.txt
```

### Step 1.3: Create Django Project

```bash
# Create project (make sure you're in Exercise directory)
django-admin startproject blogproject .

# Verify structure
ls
# Should see: blogproject/, manage.py, requirements.txt, venv/

# Run initial migration
python manage.py migrate

# Test server
python manage.py runserver
# Visit http://127.0.0.1:8000/ - should see Django welcome page
```

### Step 1.4: Create Blog App

```bash
# Create blog app
python manage.py startapp blog

# Check structure
ls blog/
# Should see: admin.py, apps.py, models.py, views.py, etc.
```

### Step 1.5: Configure Settings

Edit `blogproject/settings.py`:

```python
# Add 'blog' to INSTALLED_APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog',  # Add this line
]
```

## Part 2: Create Models

### Step 2.1: Define BlogPost Model

Edit `blog/models.py`:

```python
from django.db import models
from django.utils import timezone

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=100)
    published_date = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-published_date']
```

### Step 2.2: Create and Run Migrations

```bash
# Create migration files
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

### Step 2.3: Register Model in Admin

Edit `blog/admin.py`:

```python
from django.contrib import admin
from .models import BlogPost

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'published_date', 'is_published']
    list_filter = ['is_published', 'published_date']
    search_fields = ['title', 'content', 'author']
```

### Step 2.4: Create Superuser

```bash
# Create admin superuser
python manage.py createsuperuser

# Follow prompts to create username and password
# Test admin: http://127.0.0.1:8000/admin/
```

## Part 3: Create Views

### Step 3.1: Implement Views

Edit `blog/views.py`:

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import BlogPost

# List view
def post_list(request):
    posts = BlogPost.objects.filter(is_published=True)
    return render(request, 'blog/post_list.html', {'posts': posts})

# Detail view
def post_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

# Create view
def post_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        author = request.POST.get('author')
        is_published = request.POST.get('is_published') == 'on'
        
        post = BlogPost.objects.create(
            title=title,
            content=content,
            author=author,
            is_published=is_published
        )
        messages.success(request, 'Post created successfully!')
        return redirect('post_detail', pk=post.pk)
    
    return render(request, 'blog/post_form.html')

# Update view
def post_update(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    
    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.author = request.POST.get('author')
        post.is_published = request.POST.get('is_published') == 'on'
        post.save()
        
        messages.success(request, 'Post updated successfully!')
        return redirect('post_detail', pk=post.pk)
    
    return render(request, 'blog/post_form.html', {'post': post})

# Delete view
def post_delete(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('post_list')
    
    return render(request, 'blog/post_confirm_delete.html', {'post': post})
```

## Part 4: Configure URLs

### Step 4.1: Create App URLs

Create `blog/urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/create/', views.post_create, name='post_create'),
    path('post/<int:pk>/update/', views.post_update, name='post_update'),
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),
]
```

### Step 4.2: Include App URLs in Project

Edit `blogproject/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
]
```

## Part 5: Create Templates

### Step 5.1: Create Template Directory Structure

```bash
# Create template directories
mkdir -p blog/templates/blog
mkdir -p blog/templates/base
```

### Step 5.2: Base Template

Create `blog/templates/base.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Django Blog{% endblock %}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background-color: #007bff;
            color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        .nav {
            background-color: #333;
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        .nav a {
            color: white;
            text-decoration: none;
            margin-right: 20px;
        }
        .message {
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .success {
            background-color: #d4edda;
            border-color: #c3e6cb;
            color: #155724;
        }
        .content {
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 3px;
            border: none;
            cursor: pointer;
            margin: 5px;
        }
        .btn:hover {
            background-color: #0056b3;
        }
        .btn-danger {
            background-color: #dc3545;
        }
        .btn-danger:hover {
            background-color: #c82333;
        }
        .btn-secondary {
            background-color: #6c757d;
        }
        .btn-secondary:hover {
            background-color: #5a6268;
        }
        .post {
            border-bottom: 1px solid #eee;
            padding: 20px 0;
        }
        .post h2 {
            margin-top: 0;
        }
        .post-meta {
            color: #666;
            font-size: 0.9em;
        }
        input, textarea, select {
            width: 100%;
            padding: 8px;
            margin: 5px 0;
            box-sizing: border-box;
            border: 1px solid #ddd;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Django Blog</h1>
    </div>
    
    <div class="nav">
        <a href="{% url 'post_list' %}">Home</a>
        <a href="{% url 'post_create' %}">New Post</a>
    </div>
    
    {% if messages %}
        {% for message in messages %}
            <div class="message success">
                {{ message }}
            </div>
        {% endfor %}
    {% endif %}
    
    <div class="content">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
```

### Step 5.3: Post List Template

Create `blog/templates/blog/post_list.html`:

```html
{% extends 'base.html' %}

{% block title %}Blog Posts - Django Blog{% endblock %}

{% block content %}
    <h1>Blog Posts</h1>
    
    {% if posts %}
        {% for post in posts %}
            <div class="post">
                <h2><a href="{% url 'post_detail' post.pk %}">{{ post.title }}</a></h2>
                <p>{{ post.content|truncatewords:30 }}</p>
                <p class="post-meta">
                    By {{ post.author }} on {{ post.published_date|date:"M d, Y" }}
                </p>
                <div>
                    <a href="{% url 'post_detail' post.pk %}" class="btn">Read More</a>
                    <a href="{% url 'post_update' post.pk %}" class="btn btn-secondary">Edit</a>
                    <a href="{% url 'post_delete' post.pk %}" class="btn btn-danger">Delete</a>
                </div>
            </div>
        {% endfor %}
    {% else %}
        <p>No posts available yet.</p>
    {% endif %}
    
    <a href="{% url 'post_create' %}" class="btn">Create New Post</a>
{% endblock %}
```

### Step 5.4: Post Detail Template

Create `blog/templates/blog/post_detail.html`:

```html
{% extends 'base.html' %}

{% block title %}{{ post.title }} - Django Blog{% endblock %}

{% block content %}
    <article>
        <h1>{{ post.title }}</h1>
        <p class="post-meta">
            By {{ post.author }} on {{ post.published_date|date:"M d, Y" }}
        </p>
        <p>{{ post.content|linebreaks }}</p>
    </article>
    
    <div>
        <a href="{% url 'post_list' %}" class="btn btn-secondary">Back to List</a>
        <a href="{% url 'post_update' post.pk %}" class="btn">Edit</a>
        <a href="{% url 'post_delete' post.pk %}" class="btn btn-danger">Delete</a>
    </div>
{% endblock %}
```

### Step 5.5: Post Form Template

Create `blog/templates/blog/post_form.html`:

```html
{% extends 'base.html' %}

{% block title %}{% if post %}Edit{% else %}Create{% endif %} Post - Django Blog{% endblock %}

{% block content %}
    <h1>{% if post %}Edit Post{% else %}Create New Post{% endif %}</h1>
    
    <form method="post">
        <div>
            <label for="title">Title:</label>
            <input type="text" id="title" name="title" value="{{ post.title }}" required>
        </div>
        
        <div>
            <label for="content">Content:</label>
            <textarea id="content" name="content" rows="10" required>{{ post.content }}</textarea>
        </div>
        
        <div>
            <label for="author">Author:</label>
            <input type="text" id="author" name="author" value="{{ post.author }}" required>
        </div>
        
        <div>
            <label>
                <input type="checkbox" name="is_published" {% if post.is_published %}checked{% endif %}>
                Publish
            </label>
        </div>
        
        <div>
            <button type="submit" class="btn">{% if post %}Update{% else %}Create{% endif %} Post</button>
            <a href="{% if post %}{% url 'post_detail' post.pk %}{% else %}{% url 'post_list' %}{% endif %}" class="btn btn-secondary">Cancel</a>
        </div>
    </form>
{% endblock %}
```

### Step 5.6: Delete Confirmation Template

Create `blog/templates/blog/post_confirm_delete.html`:

```html
{% extends 'base.html' %}

{% block title %}Delete Post - Django Blog{% endblock %}

{% block content %}
    <h1>Delete Post</h1>
    
    <p>Are you sure you want to delete "{{ post.title }}"?</p>
    
    <form method="post">
        {% csrf_token %}
        <button type="submit" class="btn btn-danger">Yes, Delete</button>
        <a href="{% url 'post_detail' post.pk %}" class="btn btn-secondary">Cancel</a>
    </form>
{% endblock %}
```

## Part 6: Testing

### Step 6.1: Run Tests

```bash
# Run the server
python manage.py runserver

# Test the following:
# 1. Visit http://127.0.0.1:8000/
# 2. Click "New Post" to create a post
# 3. View the created post
# 4. Edit the post
# 5. Delete the post
# 6. Test admin at http://127.0.0.1:8000/admin/
```

## Bonus Tasks

1. Add pagination to post list
2. Add search functionality
3. Add categories to posts
4. Improve styling with CSS framework
5. Add image upload feature
6. Implement comment system

## Troubleshooting

**Templates not found**: Check TEMPLATES setting in settings.py
**URLs not working**: Run `python manage.py check` to find issues
**Database errors**: Delete db.sqlite3 and run migrations again
**No CSS**: Check STATIC_URL in settings.py

## Next Steps

1. Test all CRUD operations
2. Create sample posts
3. Customize styling
4. Add more features
5. Read Django documentation
6. Practice with more exercises

