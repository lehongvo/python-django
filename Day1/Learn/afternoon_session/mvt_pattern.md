# Django MVT Pattern Explained

## Overview

Django uses the **Model-View-Template (MVT)** pattern, a variation of the traditional MVC pattern.

## MVT vs MVC

### Traditional MVC (Model-View-Controller)
```
User Request → Controller → Model ←→ Database
                      ↓
                   View (returns response)
```

### Django MVT (Model-View-Template)
```
User Request → URL Router → View → Template (returns HTML)
                      ↓          ↓
                  Model ←→ Database
```

## The Three Components

### 1. Model (M)

**Purpose**: Represents data structure and business logic.

**Location**: `app_name/models.py`

**Responsibilities**:
- Define data structure
- Interact with database
- Define business logic
- Handle data validation

**Example**:

```python
from django.db import models

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

### 2. View (V)

**Purpose**: Contains the business logic and processes data.

**Location**: `app_name/views.py`

**Responsibilities**:
- Handle HTTP requests
- Process data
- Query the model
- Pass data to template
- Return HTTP responses

**Example**:

```python
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import BlogPost

def index(request):
    """Display list of blog posts"""
    posts = BlogPost.objects.filter(is_published=True)
    context = {
        'posts': posts
    }
    return render(request, 'blog/index.html', context)

def post_detail(request, post_id):
    """Display single post detail"""
    post = get_object_or_404(BlogPost, id=post_id)
    context = {
        'post': post
    }
    return render(request, 'blog/detail.html', context)
```

### 3. Template (T)

**Purpose**: Defines the presentation layer (HTML).

**Location**: `app_name/templates/`

**Responsibilities**:
- Define HTML structure
- Display data from views
- Handle presentation logic
- Create user interface

**Example**:

```html
<!-- templates/blog/index.html -->
{% extends 'base.html' %}

{% block content %}
    <h1>Blog Posts</h1>
    {% for post in posts %}
    <article>
        <h2>{{ post.title }}</h2>
        <p>{{ post.content|truncatewords:30 }}</p>
        <small>By {{ post.author }} on {{ post.published_date }}</small>
        <a href="{% url 'post_detail' post.id %}">Read more</a>
    </article>
    {% empty %}
    <p>No posts available.</p>
    {% endfor %}
{% endblock %}
```

## Complete Flow Example

### Step 1: URL Configuration

```python
# myproject/urls.py
from django.contrib import admin
from django.urls import path
from blog import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
]
```

### Step 2: Model Definition

```python
# blog/models.py
from django.db import models

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
```

### Step 3: View Logic

```python
# blog/views.py
from django.shortcuts import render
from .models import BlogPost

def index(request):
    posts = BlogPost.objects.all()[:5]
    return render(request, 'blog/index.html', {'posts': posts})
```

### Step 4: Template

```html
<!-- blog/templates/blog/index.html -->
<h1>Latest Posts</h1>
{% for post in posts %}
    <div>
        <h2>{{ post.title }}</h2>
        <p>{{ post.content }}</p>
    </div>
{% endfor %}
```

## Request Flow in Django

```
1. User visits: http://example.com/post/1/

2. URL Router (urls.py)
   ├─ Matches URL pattern
   └─ Calls view function: views.post_detail

3. View (views.py)
   ├─ Receives request and post_id=1
   ├─ Queries database via Model
   └─ Gets BlogPost with id=1

4. Model (models.py)
   ├─ Interacts with database
   └─ Returns Post object

5. View processes data
   ├─ Creates context dictionary
   └─ Renders template with context

6. Template (HTML)
   ├─ Receives context data
   ├─ Processes Django template syntax
   └─ Generates final HTML

7. Response
   └─ Returns HTML to user's browser
```

## Class-Based Views

Django also supports **Class-Based Views** (CBV):

```python
from django.views.generic import ListView, DetailView
from .models import BlogPost

class PostListView(ListView):
    model = BlogPost
    template_name = 'blog/list.html'
    context_object_name = 'posts'
    paginate_by = 10

class PostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/detail.html'
    context_object_name = 'post'
```

## Function-Based vs Class-Based Views

| Feature | Function-Based | Class-Based |
|---------|---------------|-------------|
| **Simplicity** | ✅ Simple | ❌ More complex |
| **Flexibility** | ✅ Very flexible | ✅ Reusable |
| **Battery** | ❌ Write everything | ✅ Built-in features |
| **Learning** | ✅ Easy to learn | ❌ Steeper curve |
| **Use Case** | Simple, one-off | Complex, reusable |

## Template Language

### Variables
```html
{{ variable_name }}
{{ post.title }}
{{ user.get_full_name }}
```

### Tags
```html
{% if user.is_authenticated %}
    <p>Welcome, {{ user.username }}!</p>
{% endif %}

{% for item in items %}
    <li>{{ item }}</li>
{% endfor %}
```

### Filters
```html
{{ name|upper }}
{{ post.date|date:"Y-m-d" }}
{{ content|truncatewords:50 }}
```

### Comments
```html
{# This is a comment #}
```

## Best Practices

1. **Models**: Keep business logic in models
2. **Views**: Keep views thin, delegate to models
3. **Templates**: Keep presentation logic only
4. **Separation**: Don't mix concerns
5. **Reusability**: Use generic views when possible

## Quick Reference

```python
# MODELS: Data & Business Logic
class ModelName(models.Model):
    field = models.FieldType()

# VIEWS: Request Handling
def view_name(request):
    data = ModelName.objects.get(id=1)
    return render(request, 'template.html', {'data': data})

# TEMPLATES: Presentation
{{ variable }}
{% tag %}
{{ value|filter }}
```

## Summary

- **Model**: Data structure and database operations
- **View**: Business logic and request handling
- **Template**: HTML presentation
- **Flow**: URL → View → Model → Database → View → Template → Response

The MVT pattern separates concerns, making Django applications easy to maintain and scale.

