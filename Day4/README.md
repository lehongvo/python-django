# 🎓 Day 4 - Django Template Language

## 📚 Tổng Quan

Day 4 tập trung vào việc học Django Template Language (DTL) và các kỹ thuật xử lý frontend trong Django.

## 📁 Cấu Trúc

```
Day4/
├── Learn/                    # Tài liệu học tập
│   ├── README.md            # Hướng dẫn học
│   ├── 00_DJANGO_TEMPLATE_LANGUAGE.md
│   ├── 01_TEMPLATE_INHERITANCE.md
│   ├── 02_TEMPLATE_TAGS_FILTERS.md
│   ├── 03_STATIC_FILES.md
│   ├── 04_CONTEXT_PROCESSORS.md
│   ├── 05_CUSTOM_TEMPLATE_TAGS.md
│   ├── 06_MEDIA_FILES.md
│   └── 07_FRONTEND_INTEGRATION.md
│
└── Exercise/                 # Bài tập thực hành
    ├── README.md            # Project overview
    ├── DAY4_GUIDE.md        # Hướng dẫn Day 4
    ├── ecommerce_project/   # Django project
    ├── store/               # Django app
    │   ├── context_processors.py  ✨ NEW
    │   ├── templatetags/         ✨ NEW
    │   │   ├── __init__.py
    │   │   ├── store_filters.py
    │   │   └── store_tags.py
    │   ├── models.py
    │   ├── views.py
    │   ├── templates/store/
    │   ├── static/store/
    │   └── media/
    └── docker-compose.yml    # Docker setup
```

## 🎯 Mục Tiêu Học Tập

Sau khi hoàn thành Day 4, bạn sẽ:

- ✅ Hiểu và sử dụng template inheritance
- ✅ Áp dụng template tags và filters
- ✅ Quản lý static files
- ✅ Tạo custom context processors ✨ NEW
- ✅ Tạo custom template tags ✨ NEW
- ✅ Xử lý media files (upload/display)
- ✅ Tích hợp CSS frameworks
- ✅ Tích hợp JavaScript với AJAX
- ✅ Tạo responsive UI

## 📖 Nội Dung Học

### Morning (4h) 🌅

1. **Template Inheritance** - Kế thừa template
2. **Template Tags & Filters** - Tags và filters
3. **Static Files Management** - Quản lý static files

### Afternoon (4h) 🌆

4. **Context Processors** - Context processors ✨ NEW
5. **Custom Template Tags** - Custom tags ✨ NEW
6. **Media Files Handling** - Xử lý media files
7. **Frontend Integration** - Tích hợp frontend

## 🚀 Bắt Đầu

### Step 1: Đọc Tài Liệu
```bash
cd /Users/user/Desktop/python-django/Day4/Learn
cat README.md
```

### Step 2: Xem Hướng Dẫn Bài Tập
```bash
cd /Users/user/Desktop/python-django/Day4/Exercise
cat DAY4_GUIDE.md
```

### Step 3: Khởi Động Project
```bash
cd Day4/Exercise
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py seed_store --categories 20 --products 2000
```

### Step 4: Truy Cập Website
- Website: http://localhost:8001
- Admin: http://localhost:8001/admin

## ✨ Tính Năng Mới (Day 4)

### 1. Context Processors ✅
```python
# store/context_processors.py
def site_settings(request):
    return {
        'site_name': 'TechStore 2025',
        'current_year': 2024,
    }
```

**Sử dụng trong template:**
```django
{{ site_name }} - {{ current_year }}
{{ cart_count }} items in cart
```

### 2. Custom Filters ✅
```python
# store/templatetags/store_filters.py
@register.filter
def format_vnd(amount):
    return f"{int(amount):,} đ"
```

**Sử dụng:**
```django
{% load store_filters %}
{{ product.price|format_vnd }}
{{ product|in_stock }}
{{ product.discount_percent }}% off
```

### 3. Custom Tags ✅
```python
# store/templatetags/store_tags.py
@register.simple_tag
def current_year():
    return datetime.now().year

@register.inclusion_tag('store/components/product_card.html')
def show_product_card(product):
    return {'product': product}
```

**Sử dụng:**
```django
{% load store_tags %}
© {% current_year %}
{% show_product_card product %}
```

## 📝 Checklist

### Đã Hoàn Thành ✅
- [x] Tạo Context Processors
- [x] Tạo Custom Template Tags
- [x] Tạo Custom Filters
- [x] Update settings.py
- [x] Cấu trúc project

### Cần Thực Hành 🎯
- [ ] Sử dụng context processors trong templates
- [ ] Sử dụng custom filters trong templates
- [ ] Tạo inclusion tags components
- [ ] Improve static files organization
- [ ] Add thumbnails for images

## 📚 Tài Liệu Tham Khảo

- [Django Template Documentation](https://docs.djangoproject.com/en/4.2/ref/templates/)
- [Custom Template Tags](https://docs.djangoproject.com/en/4.2/howto/custom-template-tags/)
- [Context Processors](https://docs.djangoproject.com/en/4.2/ref/templates/api/)

---

**Happy Learning! 🚀**
