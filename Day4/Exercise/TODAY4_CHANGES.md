# Day 4 - Cải Thiện Source Code

## ✅ Đã Hoàn Thành

### 1. Context Processors ✅
- ✅ Tạo `store/context_processors.py` với 4 processors
- ✅ Thêm vào `settings.py`
- ❌ Chưa áp dụng trong templates

### 2. Custom Template Tags ✅
- ✅ Tạo `store/templatetags/store_filters.py`
- ✅ Tạo `store/templatetags/store_tags.py`
- ❌ Chưa load trong templates
- ❌ Chưa tạo inclusion tag components

### 3. Static Files Organization
- ❌ Chưa tổ chức lại CSS files
- ✅ Đã có JavaScript (cart.js)

### 4. Thumbnails for Images
- ❌ Chưa implement thumbnail generation

## 📝 Cần Làm

### 1. Áp dụng Context Processors trong Templates

**Cập nhật base.html:**
```django
<title>{% block title %}{{ site_name }} - Premium E-commerce{% endblock %}</title>

<header>
    <h1>{{ site_name }}</h1>
    <p>{{ site_tagline }}</p>
    <p>&copy; {{ current_year }} {{ site_name }}</p>
</header>

{# Navbar với categories #}
{% for category in nav_categories %}
    <a href="{% url 'store:category_detail' category.slug %}">{{ category.name }}</a>
{% endfor %}

{# Cart badge với count #}
<span class="cart-badge">{{ cart_count }} items</span>
```

### 2. Load Custom Tags trong Templates

**Cập nhật tất cả templates:**
```django
{% load static %}
{% load store_filters %}
{% load store_tags %}
```

**Sử dụng filters:**
```django
{{ product.price|format_vnd }}
{{ product|in_stock }}
{{ product.discount_percent }}% off
```

### 3. Tạo Inclusion Tag Components

**Tạo templates/components/ directory**
- `product_card.html` - Product card component
- `pagination.html` - Pagination component
- `user_badge.html` - User badge component

### 4. Tổ Chức Static Files

**Cấu trúc mới:**
```
static/store/
├── css/
│   ├── base.css
│   ├── components/
│   │   ├── cards.css
│   │   └── forms.css
│   └── pages/
│       └── products.css
├── js/
│   ├── cart.js
│   ├── utils.js
│   └── components/
│       └── product.js
└── images/
    └── placeholders/
```

### 5. Thêm Thumbnails

**Trong models.py hoặc views.py:**
```python
from PIL import Image

def create_thumbnail(image_path, size=(300, 300)):
    img = Image.open(image_path)
    img.thumbnail(size, Image.LANCZOS)
    
    # Generate thumbnail path
    thumb_path = image_path.replace('.jpg', '_thumb.jpg')
    img.save(thumb_path)
    return thumb_path
```

## 🚀 Hướng Dẫn Test

### Bước 1: Restart Container
```bash
cd Day4/Exercise
docker-compose restart web
```

### Bước 2: Test Context Processors
Truy cập bất kỳ trang nào và kiểm tra:
- Site name hiển thị: `{{ site_name }}`
- Cart count hiển thị: `{{ cart_count }}`
- Categories trong nav: `{% for cat in nav_categories %}`

### Bước 3: Test Custom Filters
Trong product templates, thêm:
```django
{% load store_filters %}
{{ product.price|format_vnd }}
```

### Bước 4: Test Custom Tags
```django
{% load store_tags %}
© {% current_year %}
```

## 📊 Progress

- [x] Tạo context processors
- [x] Tạo custom template tags
- [x] Tạo custom filters
- [ ] Áp dụng context processors trong templates (0%)
- [ ] Load custom tags trong templates (0%)
- [ ] Tạo inclusion tag components (0%)
- [ ] Tổ chức static files (0%)
- [ ] Thêm thumbnails (0%)

---

**Next Steps:** 
1. Update base.html để sử dụng context processors
2. Add {% load %} tags vào templates
3. Tạo inclusion tag components
4. Organize static files structure


