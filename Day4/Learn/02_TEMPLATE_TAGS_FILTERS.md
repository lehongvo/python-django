# Template Tags & Filters

## 📖 Template Tags

Template tags thực hiện logic trong template và được viết trong `{% ... %}`.

### 1. If/Else Tags

```django
{% if user.is_authenticated %}
    <p>Welcome, {{ user.username }}!</p>
{% else %}
    <p>Please <a href="/login/">login</a></p>
{% endif %}

{# Multiple conditions #}
{% if age >= 18 %}
    <p>Adult</p>
{% elif age >= 13 %}
    <p>Teen</p>
{% else %}
    <p>Child</p>
{% endif %}

{# Boolean operators #}
{% if user.is_staff and user.is_active %}
    <p>Admin access granted</p>
{% endif %}

{% if user.is_staff or perms.myapp.can_edit %}
    <p>Has permission</p>
{% endif %}

{% if not user.is_authenticated %}
    <p>Not logged in</p>
{% endif %}
```

### 2. For Loop Tags

```django
{# Basic for loop #}
{% for item in items %}
    <li>{{ item }}</li>
{% endfor %}

{# With empty block #}
{% for product in products %}
    <div>{{ product.name }}</div>
{% empty %}
    <p>No products found</p>
{% endfor %}

{# With index #}
{% for item in items %}
    <p>{{ forloop.counter }}. {{ item }}</p>
    {# or forloop.counter0 (starts at 0) #}
{% endfor %}

{# Access parent loop #}
{% for category in categories %}
    <h2>{{ category.name }}</h2>
    {% for product in category.products.all %}
        <p>{{ forloop.parentloop.counter }}.{{ forloop.counter }} {{ product.name }}</p>
    {% endfor %}
{% endfor %}

{# Reversed loop #}
{% for item in items|reversed %}
    <li>{{ item }}</li>
{% endfor %}

{# First and last #}
{% for item in items %}
    {% if forloop.first %}
        <p class="first">⭐ {{ item }}</p>
    {% elif forloop.last %}
        <p class="last">👉 {{ item }}</p>
    {% else %}
        <p>{{ item }}</p>
    {% endif %}
{% endfor %}
```

### 3. URL Tags

```django
{# Named URL #}
<a href="{% url 'app_name:view_name' %}">Link</a>

{# With parameters #}
<a href="{% url 'app_name:detail' pk=object.id %}">Detail</a>

{# With multiple params #}
<a href="{% url 'app_name:filter' category='electronics' page=2 %}">Electronics</a>

{# With string parameters #}
<a href="{% url 'app_name:detail' slug=object.slug %}">{{ object.title }}</a>

{# In templates without app_name #}
<a href="{% url 'detail' 123 %}">Detail</a>
```

### 4. Include Tags

```django
{# Include another template #}
{% include 'components/header.html' %}

{# With variables #}
{% include 'components/card.html' with title="Product" content=product.description %}

{# Pass variables #}
{% include 'components/user_card.html' with user=current_user %}

{# Include only #}
{% include 'components/sidebar.html' only %}

{# Allow missing files #}
{% include 'optional_widget.html' %}
```

### 5. Static Files Tags

```django
{% load static %}

{# CSS files #}
<link rel="stylesheet" href="{% static 'css/style.css' %}">

{# JavaScript files #}
<script src="{% static 'js/app.js' %}"></script>

{# Images #}
<img src="{% static 'images/logo.png' %}" alt="Logo">

{# In context #}
<img src="{% static product.image_url %}" alt="{{ product.name }}">
```

### 6. CSRF Token

```django
<form method="post">
    {% csrf_token %}
    <input type="text" name="username">
    <button type="submit">Submit</button>
</form>
```

### 7. Comment

```django
{# Single line comment #}

{# Multi-line
comment
can be
here #}
```

## 🔧 Built-in Filters

### String Filters

```django
{# Case #}
{{ name|upper }}           {# JOHN DOE #}
{{ name|lower }}           {# john doe #}
{{ name|title }}           {# John Doe #}
{{ name|capfirst }}        {# John doe #}

{# Truncation #}
{{ description|truncatewords:10 }}     {# First 10 words #}
{{ description|truncatechars:50 }}     {# First 50 chars #}

{# Length #}
{{ text|length }}          {# 123 #}
{{ text|length_is:"10" }}  {# True/False #}

{# Join #}
{{ list|join:", " }}       {# item1, item2, item3 #}

{# Split #}
{{ tags|split:"," }}       {# ['tag1', 'tag2'] #}

{# Remove/Replace #}
{{ text|removetags:"p" }}  {# Remove <p> tags #}
{{ text|striptags }}       {# Remove all tags #}
{{ text|safe }}            {# Render HTML safely #}

{# Strip #}
{{ text|stripspaces }}     {# Remove extra spaces #}
{{ text|trim }}            {# Trim whitespace #}

{# Word count #}
{{ text|wordcount }}       {# Count words #}
```

### Date & Time Filters

```django
{# Format date #}
{{ date|date:"Y-m-d" }}              {# 2024-01-15 #}
{{ date|date:"F d, Y" }}             {# January 15, 2024 #}
{{ date|date:"SHORT_DATETIME_FORMAT" }}  {# 1/15/2024 #}

{# Time #}
{{ time|time:"H:i" }}                 {# 14:30 #}

{# Timesince/Timetill #}
{{ date|timesince }}                  {# "3 hours ago" #}
{{ date|timesince:another_date }}    {# "2 hours ago" #}

{# Natural time #}
{{ date|naturaltime }}                {# Human readable #}
```

### Number Filters

```django
{# Format #}
{{ price|floatformat }}          {# 99.0 #}
{{ price|floatformat:2 }}        {# 99.99 #}
{{ price|floatformat:"0" }}      {# 100 #}

{# Math #}
{{ price|add:"10" }}             {# price + 10 #}
{{ price|mul:"1.5" }}            {# price * 1.5 #}

{# Filesize #}
{{ file.size|filesizeformat }}   {# "1.5 MB" #}

{# Comma separator #}
{{ large_number|intcomma }}      {# 1,234,567 #}
```

### Other Useful Filters

```django
{# Default #}
{{ value|default:"Not available" }}
{{ value|default_if_none:"N/A" }}

{# Yes/No #}
{{ is_active|yesno:"Yes,No" }}      {# Yes/No #}
{{ is_published|yesno:"✅,❌" }}    {# ✅/❌ #}

{# Make list #}
{{ string|make_list }}              {# ['a', 'b', 'c'] #}

{# Slice #}
{{ items|slice:":5" }}               {# First 5 items #}
{{ items|slice:"5:10" }}            {# Items 5-10 #}

{# Random #}
{{ items|random }}                   {# Random item #}

{# Linebreaks #}
{{ text|linebreaks }}               {# Convert \n to <br> #}
{{ text|linebreaksbr }}             {# Convert \n to <br><br> #}

{# Phone #}
{{ phone|phone2numeric }}           {# Convert to numbers #}

{# Slugify #}
{{ title|slugify }}                 {# "My Title" → "my-title" #}

{# URLize #}
{{ text|urlize }}                   {# Convert URLs to links #}
{{ text|urlizetrunc:20 }}          {# URLs truncated #}

{# Escape #}
{{ content|escape }}                {# Escape HTML #}
{{ content|force_escape }}          {# Force escape #}
```

## 📝 Ví Dụ Thực Tế

### E-commerce Product List

```django
{% for product in products %}
    <div class="product-card">
        <img src="{% static product.image %}" alt="{{ product.name }}">
        <h3>{{ product.name|title }}</h3>
        <p>{{ product.description|truncatewords:15 }}</p>
        
        {% if product.in_stock %}
            <span class="badge success">In Stock</span>
        {% else %}
            <span class="badge danger">Out of Stock</span>
        {% endif %}
        
        <div class="price">
            ${{ product.price|floatformat:2 }}
        </div>
        
        <button onclick="addToCart({{ product.id }})">
            Add to Cart
        </button>
        
        <p class="meta">
            Added {{ product.created_date|timesince }} ago
        </p>
    </div>
{% empty %}
    <p>No products available</p>
{% endfor %}
```

### Blog Post Display

```django
<article>
    <h1>{{ post.title }}</h1>
    <p class="meta">
        Published on {{ post.published_date|date:"F d, Y" }}
        by {{ post.author|upper }}
    </p>
    
    <div class="content">
        {{ post.content|linebreaks|safe }}
    </div>
    
    <div class="tags">
        {% for tag in post.tags.all %}
            <span class="tag">{{ tag.name|slugify }}</span>
        {% endfor %}
    </div>
</article>
```

### User Profile

```django
<div class="profile">
    <img src="{{ user.profile.avatar.url }}" alt="{{ user.username }}">
    <h2>{{ user.get_full_name|default:user.username }}</h2>
    
    {% if user.is_staff %}
        <span class="badge admin">Admin</span>
    {% endif %}
    
    <p>Member since {{ user.date_joined|date:"Y" }}</p>
    <p>Last login: {{ user.last_login|timesince }} ago</p>
    
    <div class="stats">
        <p>Posts: {{ user.post_count|default:0 }}</p>
        <p>Comments: {{ user.comment_count|default:0 }}</p>
    </div>
</div>
```

## ✅ Checklist

- [x] Hiểu và sử dụng được If/Else tags
- [x] Sử dụng được For loop với các biến forloop
- [x] Sử dụng URL tags với parameters
- [x] Include templates
- [x] Load và sử dụng static files
- [x] Sử dụng các filters phổ biến
- [x] Format dates, numbers, strings
