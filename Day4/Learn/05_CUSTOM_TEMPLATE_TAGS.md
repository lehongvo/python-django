# Custom Template Tags & Filters

## 📖 Khái Niệm

Khi built-in tags/filters không đủ, Django cho phép tạo custom tags và filters để xử lý logic phức tạp hơn trong templates.

## 🏗️ Cấu Trúc

### Tạo thư mục templatetags

```
myapp/
├── __init__.py
├── models.py
├── views.py
└── templatetags/
    ├── __init__.py
    └── my_filters.py
```

## 🔧 Custom Filters

### Filter cơ bản

```python
# myapp/templatetags/my_filters.py
from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='times')
def multiply_times(value, arg):
    """Same as multiply, but with different name"""
    return multiply(value, arg)

@register.filter
def price_with_tax(price, tax_rate=0.1):
    """Calculate price with tax"""
    return float(price) * (1 + float(tax_rate))

@register.filter
def price_with_discount(price, discount):
    """Calculate discounted price"""
    return float(price) * (1 - float(discount) / 100)
```

**Sử dụng:**
```django
{% load my_filters %}

{{ 10|multiply:5 }}              {# 50 #}
{{ 100|price_with_tax }}         {# 110 #}
{{ 100|price_with_discount:20 }} {# 80 #}
```

### Filter với logic phức tạp

```python
@register.filter
def format_phone(phone):
    """Format phone number"""
    phone = str(phone).replace('-', '').replace(' ', '')
    if len(phone) == 10:
        return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"
    return phone

@register.filter
def truncate_smart(text, length):
    """Smart truncate that doesn't cut words"""
    if len(text) <= int(length):
        return text
    
    return text[:int(length)].rsplit(' ', 1)[0] + '...'

@register.filter
def make_range(value):
    """Make range from value"""
    return range(int(value))

@register.filter
def days_until(date):
    """Calculate days until date"""
    from datetime import date as date_class
    delta = date - date_class.today()
    return delta.days
```

**Sử dụng:**
```django
{% load my_filters %}

{{ "1234567890"|format_phone }}       {# 123-456-7890 #}
{{ text|truncate_smart:100 }}          {# Smart truncate #}
{% for i in 10|make_range %}
    {{ i }}
{% endfor %}
{{ event.date|days_until }}            {# Days until event #}
```

## 🏷️ Custom Template Tags

### Simple Tag

```python
from django import template
from datetime import datetime

register = template.Library()

@register.simple_tag
def current_time(format_string):
    """Display current time in specified format"""
    return datetime.now().strftime(format_string)

@register.simple_tag
def my_tag(a, b, *args, **kwargs):
    """Example of multiple arguments"""
    extra = kwargs.get('extra', 'nothing')
    return f'{a} + {b} = {a + b}, extra: {extra}'

@register.simple_tag
def calculate_total(price, quantity, discount=0):
    """Calculate total with discount"""
    total = float(price) * int(quantity)
    if discount:
        total *= (1 - float(discount) / 100)
    return f"${total:.2f}"
```

**Sử dụng:**
```django
{% load my_filters %}

{% current_time "%Y-%m-%d %H:%M" %}     {# 2024-01-15 14:30 #}
{% my_tag 5 10 extra="hello" %}         {# 5 + 10 = 15, extra: hello #}
{% calculate_total 10 5 discount=20 %} {# $40.00 #}
```

### Inclusion Tag

Inclusion tag render một template con và trả về HTML.

```python
@register.inclusion_tag('components/product_card.html')
def show_product(product, show_description=True):
    """Render product card"""
    return {
        'product': product,
        'show_description': show_description,
    }

@register.inclusion_tag('components/pagination.html')
def pagination(page_obj):
    """Render pagination"""
    return {
        'page_obj': page_obj,
    }

@register.inclusion_tag('components/sidebar_menu.html')
def sidebar_menu(current_url):
    """Render sidebar menu with active state"""
    menu_items = [
        {'url': '/', 'name': 'Home', 'active': current_url == '/'},
        {'url': '/products/', 'name': 'Products', 'active': '/products/' in current_url},
        {'url': '/about/', 'name': 'About', 'active': '/about/' in current_url},
    ]
    return {'menu_items': menu_items}
```

**component templates:**

```django
{# components/product_card.html #}
<div class="product-card">
    <img src="{{ product.image.url }}" alt="{{ product.name }}">
    <h3>{{ product.name }}</h3>
    {% if show_description %}
        <p>{{ product.description|truncatewords:20 }}</p>
    {% endif %}
    <p class="price">${{ product.price }}</p>
</div>
```

```django
{# components/pagination.html #}
<div class="pagination">
    {% if page_obj.has_previous %}
        <a href="?page={{ page_obj.previous_page_number }}">← Previous</a>
    {% endif %}
    
    <span>{{ page_obj.number }} of {{ page_obj.paginator.num_pages }}</span>
    
    {% if page_obj.has_next %}
        <a href="?page={{ page_obj.next_page_number }}">Next →</a>
    {% endif %}
</div>
```

**Sử dụng:**
```django
{% load my_filters %}

{# Show product card #}
{% show_product product %}

{# Show product without description #}
{% show_product product show_description=False %}

{# Pagination #}
{% pagination page_obj %}

{# Sidebar menu #}
{% sidebar_menu request.path %}
```

## 📝 Ví Dụ Thực Tế

### E-commerce Store

```python
# store/templatetags/store_filters.py
from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def format_currency(amount, currency='USD'):
    """Format amount as currency"""
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
    }
    symbol = symbols.get(currency, '$')
    return f"{symbol}{amount:,.2f}"

@register.filter
def in_stock(product):
    """Check if product is in stock"""
    return product.quantity > 0

@register.filter
def discount_percentage(original, current):
    """Calculate discount percentage"""
    if original <= 0:
        return 0
    return int((1 - current/original) * 100)

@register.simple_tag
def cart_subtotal(cart_items):
    """Calculate cart subtotal"""
    return sum(item.product.price * item.quantity for item in cart_items)

@register.inclusion_tag('store/components/product_badge.html')
def product_badge(product):
    """Show product badge (New, Sale, Out of Stock)"""
    badge = None
    is_new = (timezone.now() - product.created).days < 30
    has_discount = product.compare_price and product.compare_price > product.price
    
    if product.quantity == 0:
        badge = {'type': 'out-of-stock', 'text': 'Out of Stock'}
    elif has_discount:
        badge = {'type': 'sale', 'text': 'Sale'}
    elif is_new:
        badge = {'type': 'new', 'text': 'New'}
    
    return {'badge': badge}
```

**Template sử dụng:**
```django
{% load store_filters %}

<div class="product">
    <h3>{{ product.name }}</h3>
    
    {# Display price with currency #}
    <p class="price">{{ product.price|format_currency }}</p>
    
    {# Check stock #}
    {% if product|in_stock %}
        <span class="badge green">In Stock</span>
    {% else %}
        <span class="badge red">Out of Stock</span>
    {% endif %}
    
    {# Show discount #}
    {% if product.compare_price %}
        <p class="discount">
            Save {{ product.compare_price|discount_percentage:product.price }}%
        </p>
    {% endif %}
    
    {# Badge tag #}
    {% product_badge product %}
</div>

<div class="cart-summary">
    Subtotal: {% cart_subtotal cart_items %}
</div>
```

### Blog with Tags

```python
# blog/templatetags/blog_tags.py
from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def reading_time(content):
    """Calculate reading time"""
    words = len(content.split())
    minutes = words // 200  # Average reading speed
    return max(1, minutes)

@register.filter
def time_ago(date):
    """Human readable time ago"""
    now = timezone.now()
    diff = now - date
    
    if diff.days > 365:
        return f"{diff.days // 365} years ago"
    elif diff.days > 30:
        return f"{diff.days // 30} months ago"
    elif diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600} hours ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60} minutes ago"
    else:
        return "just now"

@register.inclusion_tag('blog/components/author_card.html')
def show_author(post):
    """Show author information"""
    return {
        'author': post.author,
        'post_count': post.author.posts.count(),
    }

@register.inclusion_tag('blog/components/related_posts.html')
def show_related_posts(post, count=5):
    """Show related posts"""
    related = post.tags.similar_objects()[:count]
    return {'posts': related}
```

**Sử dụng:**
```django
{% load blog_tags %}

<article>
    <h1>{{ post.title }}</h1>
    
    <p class="meta">
        <span>{{ post.published_date|time_ago }}</span>
        <span>{{ post.content|reading_time }} min read</span>
    </p>
    
    <div class="content">{{ post.content|safe }}</div>
    
    {# Author card #}
    {% show_author post %}
    
    {# Related posts #}
    {% show_related_posts post count=3 %}
</article>
```

## 🎯 Advanced Examples

### Lazy Loading Filter

```python
@register.filter
def lazy_image(image_url, placeholder='#'):
    """Create lazy loading image"""
    return {
        'src': image_url,
        'placeholder': placeholder,
    }
```

### CSRF Token Tag

```python
@register.simple_tag
def csrf_token_input():
    """Generate CSRF token input"""
    from django.middleware.csrf import get_token
    token = get_token()
    return f'<input type="hidden" name="csrfmiddlewaretoken" value="{token}">'
```

## ✅ Checklist

- [ ] Tạo thư mục templatetags
- [ ] Tạo custom filters
- [ ] Tạo custom simple tags
- [ ] Tạo custom inclusion tags
- [ ] Sử dụng trong templates
- [ ] Test các tags và filters
