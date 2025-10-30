# Django Template Language (DTL) - Tổng Quan

## 🎯 Mục Tiêu

- Hiểu cấu trúc và cú pháp Django Template Language
- Áp dụng template inheritance và blocks
- Sử dụng template tags và filters
- Quản lý static files và media files

## 📚 Nội Dung Học

### 1. Template Inheritance (Thừa Kế Template)

**Khái niệm:** Template inheritance cho phép tạo template base và các template con kế thừa, giúp tránh lặp code.

**Cấu trúc cơ bản:**

```django
{# base.html - Template cha #}
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Default Title{% endblock %}</title>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>

{# child.html - Template con #}
{% extends 'base.html' %}

{% block title %}My Page{% endblock %}

{% block content %}
    <h1>Welcome!</h1>
{% endblock %}
```

**Các thẻ quan trọng:**

- `{% extends 'base.html' %}` - Kế thừa template cha
- `{% block name %}{% endblock %}` - Định nghĩa block
- `{{ block.super }}` - Lấy nội dung block từ template cha

### 2. Template Tags

**Khái niệm:** Template tags là các thẻ đặc biệt của Django để thực hiện logic trong template.

**Các template tags phổ biến:**

#### a. If/Else

```django
{% if user.is_authenticated %}
    <p>Welcome, {{ user.username }}!</p>
{% else %}
    <p>Please login</p>
{% endif %}
```

#### b. For Loop

```django
{% for item in items %}
    <li>{{ item }}</li>
{% empty %}
    <p>No items found</p>
{% endfor %}
```

#### c. Include

```django
{% include 'components/header.html' %}
```

#### d. URL

```django
<a href="{% url 'app:view_name' %}">Link</a>
<a href="{% url 'app:detail' pk=object.id %}">Detail</a>
```

#### e. Static Files

```django
{% load static %}
<link rel="stylesheet" href="{% static 'css/style.css' %}">
<img src="{% static 'images/logo.png' %}" alt="Logo">
```

### 3. Template Filters

**Khái niệm:** Filters là các hàm để xử lý dữ liệu trong template.

**Các filters phổ biến:**

```django
{# String filters #}
{{ name|upper }}           {# CHỮ HOA #}
{{ name|lower }}           {# chữ thường #}
{{ name|title }}           {# Tiêu Đề #}
{{ name|truncatewords:10 }} {# Cắt từ #}
{{ name|length }}          {# Độ dài #}

{# Date filters #}
{{ date|date:"Y-m-d" }}    {# 2024-01-01 #}
{{ date|timesince }}       {# "2 hours ago" #}

{# Number filters #}
{{ price|floatformat:2 }}  {# 99.99 #}
{{ number|add:"5" }}      {# Cộng thêm #}

{# HTML filters #}
{{ content|safe }}         {# Render HTML #}
{{ content|escape }}       {# Escape HTML #}
{{ content|striptags }}    {# Xóa tags #}

{# Default value #}
{{ value|default:"N/A" }}  {# Giá trị mặc định #}
```

### 4. Context Processors

**Khái niệm:** Context processors là các hàm tự động thêm dữ liệu vào context của tất cả templates.

**Cấu hình trong settings.py:**

```python
TEMPLATES = [
    {
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

**Tạo custom context processor:**

```python
# myapp/context_processors.py
def global_settings(request):
    return {
        'site_name': 'My Website',
        'current_year': 2024,
    }
```

```python
# settings.py
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                # ... existing processors ...
                'myapp.context_processors.global_settings',
            ],
        },
    },
]
```

### 5. Custom Template Tags

**Tạo custom template tags:**

**Bước 1:** Tạo thư mục `templatetags`

```
myapp/
    __init__.py
    models.py
    views.py
    templatetags/
        __init__.py
        my_filters.py
```

**Bước 2:** Viết filter

```python
# templatetags/my_filters.py
from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    return int(value) * int(arg)

@register.filter(name='times')
def multiply_times(value, arg):
    return int(value) * int(arg)

@register.simple_tag
def my_tag(a, b, *args, **kwargs):
    return f'{a} + {b} = {a + b}'

@register.inclusion_tag('components/widget.html')
def show_widget(title):
    return {'title': title}
```

**Bước 3:** Sử dụng trong template

```django
{% load my_filters %}

{{ 10|multiply:5 }}        {# 50 #}
{{ price|times:1.1 }}      {# Giá + 10% #}
{% my_tag 5 10 %}          {# "5 + 10 = 15" #}
{% show_widget "News" %}   {# Render widget #}
```

### 6. Static Files Management

**Cấu hình static files:**

```python
# settings.py
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

**URL configuration:**

```python
# urls.py
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... your urls ...
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

**Cấu trúc thư mục:**

```
project/
    static/
        css/
            style.css
        js/
            app.js
        images/
            logo.png
    media/
        uploads/
            user_photos/
            documents/
```

**Sử dụng trong template:**

```django
{% load static %}

{% static 'css/style.css' %}
{% static 'images/logo.png' %}
```

### 7. Media Files Handling

**Upload file trong model:**

```python
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True)
  
    class Meta:
        upload_to = 'user_profiles/%Y/%m/'  # Dynamic path
```

**Form với file upload:**

```python
# forms.py
from django import forms

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'resume']
        widgets = {
            'avatar': forms.FileInput(attrs={'accept': 'image/*'}),
        }
```

**Template form:**

```django
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Upload</button>
</form>
```

**View xử lý upload:**

```python
from django.shortcuts import render, redirect
from .forms import ProfileForm

def upload_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('success')
    else:
        form = ProfileForm()
    return render(request, 'profile.html', {'form': form})
```

### 8. Frontend Integration

**Tích hợp CSS Framework (Bootstrap/Tailwind):**

```django
{# base.html #}
{% load static %}
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}My Site{% endblock %}</title>
  
    {# Bootstrap #}
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  
    {# Hoặc Tailwind #}
    <script src="https://cdn.tailwindcss.com"></script>
  
    <link rel="stylesheet" href="{% static 'css/custom.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% include 'components/navbar.html' %}
  
    <main>
        {% block content %}{% endblock %}
    </main>
  
    {% include 'components/footer.html' %}
  
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{% static 'js/app.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

**AJAX với Django:**

```javascript
// static/js/app.js
document.getElementById('myForm').addEventListener('submit', function(e) {
    e.preventDefault();
  
    fetch(this.action, {
        method: 'POST',
        body: new FormData(this),
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
    });
});

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
```

## 📝 Bài Tập Thực Hành

### Bài 1: Template Inheritance

- Tạo `base.html` với navbar, sidebar, footer
- Tạo 3 trang con kế thừa từ base
- Mỗi trang có title và content riêng

### Bài 2: Template Tags & Filters

- Hiển thị danh sách sản phẩm với filters
- Tạo filter tùy chỉnh `price_with_discount`
- Hiển thị date formatting

### Bài 3: Static Files

- Thêm CSS vào project
- Thêm JavaScript với AJAX
- Thêm images vào template

### Bài 4: Custom Template Tags

- Tạo tag `show_latest_posts`
- Tạo tag `calculate_total`
- Tạo inclusion_tag cho sidebar

### Bài 5: Media Files

- Tạo model với ImageField
- Form upload ảnh
- Hiển thị ảnh đã upload

## ✅ Checklist

- [X] Hiểu template inheritance và blocks
- [X] Sử dụng được các template tags phổ biến
- [X] Áp dụng filters để format dữ liệu
- [X] Tạo custom template tags và filters
- [X] Quản lý static files
- [X] Xử lý media files (upload/display)
- [X] Tích hợp frontend (CSS/JS) với Django

## 🔗 Tài Liệu Tham Khảo

- [Django Template Documentation](https://docs.djangoproject.com/en/4.2/ref/templates/)
- [Built-in Template Tags](https://docs.djangoproject.com/en/4.2/ref/templates/builtins/)
- [Built-in Template Filters](https://docs.djangoproject.com/en/4.2/ref/templates/builtins/)
- [Static Files](https://docs.djangoproject.com/en/4.2/howto/static-files/)
