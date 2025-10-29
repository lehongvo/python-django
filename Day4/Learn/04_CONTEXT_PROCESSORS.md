# Context Processors

## 📖 Khái Niệm

Context processors là các hàm tự động thêm dữ liệu vào context của tất cả templates. Thay vì truyền dữ liệu qua mỗi view, context processor cung cấp dữ liệu global cho toàn bộ ứng dụng.

## ⚙️ Cấu Hình Built-in Context Processors

```python
# settings.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
            ],
        },
    },
]
```

## 🎯 Built-in Context Processors

### 1. Request Processor
```django
{# context_processors.request #}
{{ request.user }}
{{ request.path }}
{{ request.GET }}
{{ request.POST }}
```

### 2. Auth Processor
```django
{# context_processors.auth #}
{{ user }}              {# Current user #}
{{ user.is_authenticated }}
{{ user.is_staff }}
{{ perms.myapp.can_edit }}
```

### 3. Messages Processor
```django
{# context_processors.messages #}
{% if messages %}
    {% for message in messages %}
        <div class="alert alert-{{ message.tags }}">
            {{ message }}
        </div>
    {% endfor %}
{% endif %}
```

## 🛠️ Tạo Custom Context Processor

### Ví Dụ 1: Global Site Settings

**Bước 1:** Tạo context processor

```python
# myapp/context_processors.py
from .models import SiteSettings, Category

def global_settings(request):
    """Provide global site settings to all templates"""
    return {
        'site_name': 'My Awesome Site',
        'site_tagline': 'Building amazing things',
        'current_year': 2024,
    }

def categories(request):
    """Provide all categories to all templates"""
    return {
        'all_categories': Category.objects.all(),
    }

def cart_count(request):
    """Provide cart item count for authenticated users"""
    if request.user.is_authenticated:
        count = request.user.cart_items.count()
    else:
        count = 0
    return {
        'cart_count': count,
    }
```

**Bước 2:** Thêm vào settings.py

```python
# settings.py
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Custom processors
                'myapp.context_processors.global_settings',
                'myapp.context_processors.categories',
                'myapp.context_processors.cart_count',
            ],
        },
    },
]
```

**Bước 3:** Sử dụng trong templates

```django
{# base.html #}
<html>
<head>
    <title>{{ site_name }}</title>
</head>
<body>
    <header>
        <h1>{{ site_name }}</h1>
        <p>{{ site_tagline }}</p>
    </header>

    <nav>
        {% for category in all_categories %}
            <a href="/category/{{ category.slug }}">{{ category.name }}</a>
        {% endfor %}
    </nav>

    <main>
        {% block content %}{% endblock %}
    </main>

    <footer>
        <p>&copy; {{ current_year }} {{ site_name }}</p>
    </footer>

    {# Cart badge #}
    <div class="cart">
        Cart ({{ cart_count }})
    </div>
</body>
</html>
```

## 📝 Ví Dụ Thực Tế

### Ví Dụ 1: E-commerce Site Settings

```python
# store/context_processors.py
from .models import Category, SiteConfig
from django.contrib.auth.models import User

def site_config(request):
    """Global site configuration"""
    try:
        config = SiteConfig.objects.get()
        return {
            'site_name': config.name,
            'site_logo': config.logo.url if config.logo else None,
            'footer_text': config.footer_text,
            'contact_email': config.contact_email,
            'contact_phone': config.contact_phone,
        }
    except SiteConfig.DoesNotExist:
        return {
            'site_name': 'Store',
            'site_logo': None,
            'footer_text': '',
            'contact_email': '',
            'contact_phone': '',
        }

def navigation_categories(request):
    """Categories for navigation menu"""
    return {
        'nav_categories': Category.objects.filter(parent=None)[:10],
    }

def user_cart(request):
    """User cart information"""
    cart_info = {
        'cart_items': [],
        'cart_total': 0,
        'cart_count': 0,
    }
    
    if request.user.is_authenticated:
        cart = request.user.cart_set.select_related('product').all()
        cart_info['cart_items'] = cart
        cart_info['cart_count'] = cart.count()
        cart_info['cart_total'] = sum(item.product.price * item.quantity for item in cart)
    
    return cart_info
```

### Ví Dụ 2: Blog Global Data

```python
# blog/context_processors.py
from .models import Post, Tag
from django.db.models import Count

def latest_posts(request):
    """Latest blog posts"""
    return {
        'latest_posts': Post.objects.published()[:5],
    }

def popular_tags(request):
    """Most popular tags"""
    return {
        'popular_tags': Tag.objects.annotate(
            post_count=Count('posts')
        ).order_by('-post_count')[:10],
    }

def archive_months(request):
    """Archive by months"""
    from django.db.models.functions import TruncMonth
    
    return {
        'archive_months': Post.objects.published().annotate(
            month=TruncMonth('published_date')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('-month'),
    }
```

### Sử dụng trong template

```django
{# base.html #}
{% load static %}
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}{{ site_name }}{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body>
    <header>
        {% if site_logo %}
            <img src="{{ site_logo }}" alt="{{ site_name }}">
        {% endif %}
        <h1>{{ site_name }}</h1>
    </header>

    <nav>
        <a href="/">Home</a>
        
        {# Categories from context processor #}
        {% for category in nav_categories %}
            <a href="/category/{{ category.slug }}">
                {{ category.name }}
            </a>
        {% endfor %}
    </nav>

    <aside>
        <h3>Latest Posts</h3>
        {% for post in latest_posts %}
            <a href="/post/{{ post.slug }}">{{ post.title }}</a>
        {% endfor %}

        <h3>Popular Tags</h3>
        {% for tag in popular_tags %}
            <a href="/tag/{{ tag.slug }}">{{ tag.name }}</a>
        {% endfor %}
    </aside>

    <main>
        {% block content %}{% endblock %}
    </main>

    <footer>
        <p>{{ footer_text }}</p>
        <p>Contact: {{ contact_email }} | {{ contact_phone }}</p>
        <p>&copy; {{ current_year }} {{ site_name }}</p>
        
        {# Cart info from context processor #}
        <div class="cart-summary">
            Items: {{ cart_count }} | Total: ${{ cart_total }}
        </div>
    </footer>
</body>
</html>
```

### Ví Dụ 3: User Preferences

```python
# users/context_processors.py
def user_preferences(request):
    """User preferences and settings"""
    preferences = {
        'theme': 'light',
        'language': 'en',
        'timezone': 'UTC',
    }
    
    if request.user.is_authenticated:
        try:
            prefs = request.user.userprofile.preferences
            preferences.update(prefs)
        except:
            pass
    
    return {
        'user_preferences': preferences,
        'user_theme': preferences['theme'],
        'user_language': preferences['language'],
    }
```

## 🎯 Best Practices

### 1. Chỉ dùng cho dữ liệu thực sự global

```python
# ✅ Good - Global data
def site_settings(request):
    return {'site_name': 'MySite'}

# ❌ Bad - Page-specific data
def product_detail(request):
    return {'product': Product.objects.first()}  # Not global!
```

### 2. Cache queries nếu cần

```python
from django.core.cache import cache

def categories(request):
    cache_key = 'all_categories'
    categories = cache.get(cache_key)
    
    if not categories:
        categories = list(Category.objects.all())
        cache.set(cache_key, categories, 3600)
    
    return {'all_categories': categories}
```

### 3. Tránh query nặng

```python
# ✅ Good - Lightweight queries
def count_items(request):
    return {'item_count': Item.objects.count()}

# ❌ Bad - Heavy queries run on EVERY page
def all_items(request):
    return {'all_items': list(Item.objects.select_related().prefetch_related())}
```

## ✅ Checklist

- [x] Hiểu khái niệm context processor
- [x] Biết các built-in context processors
- [x] Tạo custom context processor
- [x] Thêm vào settings.py
- [x] Sử dụng trong templates
- [x] Tránh query nặng
