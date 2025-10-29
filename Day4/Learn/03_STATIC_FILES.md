# Static Files Management

## 📖 Khái Niệm

Static files là các file tĩnh không thay đổi như:
- CSS stylesheets
- JavaScript files
- Images (logo, icons)
- Fonts

## ⚙️ Cấu Hình

### Settings.py

```python
# settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # For production

# Development: where to look for static files
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files (user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### URL Configuration

```python
# urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    # ... your other urls
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

## 📁 Cấu Trúc Thư Mục

```
project/
├── manage.py
├── myapp/
│   ├── static/
│   │   └── myapp/
│   │       ├── css/
│   │       │   └── style.css
│   │       ├── js/
│   │       │   └── app.js
│   │       └── images/
│   │           └── logo.png
├── static/
│   ├── css/
│   │   └── global.css
│   ├── js/
│   │   └── main.js
│   └── images/
├── media/
│   └── uploads/
└── staticfiles/  # Created after collectstatic
```

## 💻 Sử Dụng Trong Template

### 1. Load Static Files

```django
{# Load static tag once at the top #}
{% load static %}

<!DOCTYPE html>
<html>
<head>
    {# CSS #}
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
    
    {# JavaScript #}
    <script src="{% static 'js/app.js' %}"></script>
    
    {# Images #}
    <img src="{% static 'images/logo.png' %}" alt="Logo">
    
    {# From app static folder #}
    <link rel="stylesheet" href="{% static 'myapp/css/custom.css' %}">
</head>
<body>
    ...
</body>
</html>
```

### 2. Dynamic Static Files

```django
{% load static %}

{# Using variables #}
<img src="{% static product.image_url %}" alt="{{ product.name }}">

{# In CSS #}
<style>
    .header {
        background-image: url("{% static 'images/bg.jpg' %}");
    }
</style>
```

## 🎨 Ví Dụ Thực Tế

### Base Template

```django
{# templates/base.html #}
{% load static %}
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}My Site{% endblock %}</title>
    
    {# Bootstrap CDN #}
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    {# Custom CSS #}
    <link rel="stylesheet" href="{% static 'css/custom.css' %}">
    
    {# Page-specific CSS #}
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% include 'components/navbar.html' %}
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    {% include 'components/footer.html' %}
    
    {# jQuery #}
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    
    {# Bootstrap JS #}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    {# Custom JS #}
    <script src="{% static 'js/main.js' %}"></script>
    
    {# Page-specific JS #}
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### CSS File

```css
/* static/css/custom.css */
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --font-family: 'Arial', sans-serif;
}

body {
    font-family: var(--font-family);
    margin: 0;
    padding: 0;
}

.header {
    background: var(--primary-color);
    color: white;
    padding: 1rem;
}

.product-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
}

.product-card img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    border-radius: 4px;
}

.btn-custom {
    background: var(--primary-color);
    color: white;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.btn-custom:hover {
    background: #0056b3;
}
```

### JavaScript File

```javascript
// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add to cart
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.productId;
            addToCart(productId);
        });
    });

    // Search functionality
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value;
            searchProducts(query);
        });
    }
});

function addToCart(productId) {
    fetch('/api/cart/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: 1
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Added to cart!', 'success');
            updateCartBadge();
        }
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

function updateCartBadge() {
    fetch('/api/cart/count/')
        .then(response => response.json())
        .then(data => {
            document.getElementById('cart-badge').textContent = data.count;
        });
}
```

### Template Sử dụng

```django
{# templates/products.html #}
{% extends 'base.html' %}
{% load static %}

{% block extra_css %}
    <link rel="stylesheet" href="{% static 'css/products.css' %}">
{% endblock %}

{% block content %}
<div class="products-container">
    {% for product in products %}
        <div class="product-card">
            <img src="{% static product.image %}" alt="{{ product.name }}">
            <h3>{{ product.name }}</h3>
            <p class="price">${{ product.price }}</p>
            <button class="btn-custom add-to-cart" data-product-id="{{ product.id }}">
                Add to Cart
            </button>
        </div>
    {% endfor %}
</div>
{% endblock %}

{% block extra_js %}
    <script src="{% static 'js/products.js' %}"></script>
{% endblock %}
```

## 🚀 Production (Collect Static)

```bash
# Collect all static files to staticfiles/
python manage.py collectstatic --noinput

# Or in production with Docker
docker-compose exec web python manage.py collectstatic
```

## 📝 Static Files Finders

Django tìm static files theo thứ tự:

1. `STATICFILES_DIRS` - Directories to search
2. App's `static/` folder - Each installed app
3. STATIC_ROOT - Collected files (production)

```python
# settings.py
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]
```

## ✅ Checklist

- [x] Cấu hình STATIC_URL và STATIC_ROOT
- [x] Cấu hình MEDIA_URL và MEDIA_ROOT
- [x] Thêm static() vào urls.py cho development
- [x] Tạo cấu trúc thư mục static
- [x] Load static trong templates
- [x] Sử dụng static files trong CSS, JS, images
- [x] Chạy collectstatic cho production
