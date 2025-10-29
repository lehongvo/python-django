# Template Inheritance - Kế Thừa Template

## 📖 Khái Niệm

Template inheritance là kỹ thuật cho phép các template con kế thừa và mở rộng nội dung từ template cha. Điều này giúp:
- Tránh lặp lại code
- Dễ bảo trì và cập nhật
- Tái sử dụng layout chung

## 🏗️ Cấu Trúc Cơ Bản

### 1. Template Cha (Base Template)

```django
{# templates/base.html #}
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}My Website{% endblock %}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; }
        .header { background: #333; color: white; padding: 1rem; }
        .content { padding: 2rem; }
        .footer { background: #eee; padding: 1rem; text-align: center; }
    </style>
    {% block extra_css %}{% endblock %}
</head>
<body>
    <header class="header">
        <h1>{% block header %}My Website{% endblock %}</h1>
    </header>

    <nav>
        <a href="/">Home</a> | <a href="/about">About</a>
    </nav>

    <main class="content">
        {% block content %}
            <p>Default content</p>
        {% endblock %}
    </main>

    <footer class="footer">
        <p>© 2024 My Website</p>
    </footer>

    {% block extra_js %}{% endblock %}
</body>
</html>
```

### 2. Template Con Kế Thừa

```django
{# templates/home.html #}
{% extends 'base.html' %}

{% block title %}Home Page - My Website{% endblock %}

{% block header %}Welcome to Home{% endblock %}

{% block content %}
    <h2>Hello World!</h2>
    <p>This is the home page content.</p>
{% endblock %}

{% block extra_js %}
<script>
    console.log('Home page loaded');
</script>
{% endblock %}
```

### 3. Sử dụng `{{ block.super }}`

Cho phép giữ nội dung từ template cha:

```django
{# templates/base.html #}
{% block content %}
    <div class="main-content">
        Default content
    </div>
{% endblock %}

{# templates/extended.html #}
{% extends 'base.html' %}

{% block content %}
    {{ block.super }}  {# Giữ "Default content" #}
    <div class="additional-content">
        Additional content here
    </div>
{% endblock %}
```

## 📝 Ví Dụ Chi Tiết

### Ví Dụ 1: Website E-commerce

**base.html:**
```django
{# templates/store/base.html #}
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}TechStore{% endblock %}</title>
    <link rel="stylesheet" href="https://cdn.tailwindcss.com">
</head>
<body class="bg-gray-50">
    <nav class="bg-blue-600 text-white p-4">
        <div class="container mx-auto flex justify-between items-center">
            <a href="/" class="text-2xl font-bold">TechStore</a>
            <div>
                <a href="/cart" class="mr-4">Cart</a>
                <a href="/account">Account</a>
            </div>
        </div>
    </nav>

    <main class="container mx-auto py-8">
        {% block content %}{% endblock %}
    </main>

    <footer class="bg-gray-800 text-white text-center py-4 mt-12">
        <p>&copy; 2024 TechStore. All rights reserved.</p>
    </footer>

    <script src="https://cdn.tailwindcss.com"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

**product_list.html:**
```django
{# templates/store/product_list.html #}
{% extends 'store/base.html' %}

{% block title %}Products - TechStore{% endblock %}

{% block content %}
<div class="grid grid-cols-3 gap-4">
    {% for product in products %}
        <div class="bg-white rounded-lg shadow p-4">
            <img src="{{ product.image }}" alt="{{ product.name }}" class="w-full h-48 object-cover">
            <h3 class="text-xl font-bold mt-2">{{ product.name }}</h3>
            <p class="text-gray-600">{{ product.description|truncatewords:20 }}</p>
            <p class="text-blue-600 font-bold mt-2">${{ product.price }}</p>
        </div>
    {% endfor %}
</div>
{% endblock %}
```

**product_detail.html:**
```django
{# templates/store/product_detail.html #}
{% extends 'store/base.html' %}

{% block title %}{{ product.name }} - TechStore{% endblock %}

{% block content %}
<div class="max-w-4xl mx-auto">
    <div class="grid grid-cols-2 gap-8">
        <div>
            <img src="{{ product.image }}" alt="{{ product.name }}" class="w-full rounded-lg">
        </div>
        <div>
            <h1 class="text-3xl font-bold">{{ product.name }}</h1>
            <p class="text-gray-600 mt-2">{{ product.description }}</p>
            <p class="text-3xl font-bold text-blue-600 mt-4">${{ product.price }}</p>
            <button class="bg-blue-600 text-white px-6 py-3 rounded mt-4">
                Add to Cart
            </button>
        </div>
    </div>
</div>

{% block scripts %}
<script>
    // Product-specific JavaScript
    console.log('Product ID: {{ product.id }}');
</script>
{% endblock %}
{% endblock %}
```

### Ví Dụ 2: Blog Website

**base.html:**
```django
{# templates/blog/base.html #}
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}My Blog{% endblock %}</title>
</head>
<body>
    <header>
        <h1>{% block site_title %}My Blog{% endblock %}</h1>
        <nav>
            <a href="/">Home</a> |
            <a href="/posts">Posts</a> |
            <a href="/about">About</a>
        </nav>
    </header>

    <aside>
        {% block sidebar %}
            <h3>Categories</h3>
            <ul>
                <li>Tech</li>
                <li>News</li>
                <li>Sport</li>
            </ul>
        {% endblock %}
    </aside>

    <main>
        {% block content %}{% endblock %}
    </main>

    <footer>
        {% block footer %}
            <p>&copy; 2024 My Blog</p>
        {% endblock %}
    </footer>
</body>
</html>
```

**post_detail.html:**
```django
{# templates/blog/post_detail.html #}
{% extends 'blog/base.html' %}

{% block title %}{{ post.title }} - My Blog{% endblock %}

{% block content %}
<article>
    <h1>{{ post.title }}</h1>
    <p class="meta">
        By {{ post.author }} | {{ post.published_date|date:"F d, Y" }}
    </p>
    <div class="content">
        {{ post.content|safe }}
    </div>
</article>
{% endblock %}

{% block sidebar %}
    {{ block.super }}
    <h3>Related Posts</h3>
    <ul>
        {% for related in related_posts %}
            <li><a href="/posts/{{ related.slug }}">{{ related.title }}</a></li>
        {% endfor %}
    </ul>
{% endblock %}
```

## 🎯 Best Practices

### 1. Đặt tên Block rõ ràng

```django
{# ❌ Bad #}
{% block x %}{% endblock %}

{# ✅ Good #}
{% block extra_css %}{% endblock %}
{% block page_content %}{% endblock %}
{% block custom_scripts %}{% endblock %}
```

### 2. Sử dụng default content

```django
{% block title %}Default Title{% endblock %}

{% block meta_description %}Default description{% endblock %}
```

### 3. Tổ chức cấu trúc blocks

```django
{# base.html #}
<!DOCTYPE html>
<html>
<head>
    {% block meta %}{% endblock %}
    {% block css %}{% endblock %}
</head>
<body>
    {% block navbar %}{% endblock %}
    {% block content %}{% endblock %}
    {% block footer %}{% endblock %}
    {% block scripts %}{% endblock %}
</body>
</html>
```

### 4. Sử dụng Include

```django
{# base.html #}
{% include 'components/navbar.html' %}
{% include 'components/footer.html' %}

{# components/navbar.html #}
<nav>
    <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/about">About</a></li>
    </ul>
</nav>
```

## 🏋️ Bài Tập Thực Hành

### Bài 1: Tạo Layout Base
- Tạo `base.html` với header, sidebar, footer
- Header có logo và navigation
- Sidebar có widget
- Footer có copyright

### Bài 2: Tạo 3 Trang Con
- `home.html` - Trang chủ với hero section
- `products.html` - Danh sách sản phẩm
- `contact.html` - Trang liên hệ

### Bài 3: Nested Blocks
- Tạo 3 levels inheritance
- Level 1: base.html
- Level 2: base_blog.html (extends base.html)
- Level 3: post_detail.html (extends base_blog.html)

## ✅ Checklist

- [ ] Hiểu khái niệm template inheritance
- [ ] Sử dụng được `{% extends %}`
- [ ] Sử dụng được `{% block %}` và `{{ block.super }}`
- [ ] Tạo được base template
- [ ] Tạo được child templates
- [ ] Tổ chức được cấu trúc thư mục templates
