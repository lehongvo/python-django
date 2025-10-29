# 🎓 Day 4 - Django Template Language - Practice Guide

## 📚 Tổng Quan

Project này đã có sẵn cấu trúc cơ bản với:
- ✅ Template inheritance (base.html)
- ✅ Tailwind CSS integration
- ✅ Models, Views, URLs hoàn chỉnh
- ✅ Static files setup
- ✅ Media files support

## 🎯 Nhiệm Vụ Day 4

Bạn sẽ cải thiện project này bằng cách áp dụng các kiến thức từ Day 4 Learn:

### Morning (4h) 🌅

#### 1. Template Inheritance & Blocks ✅
Project đã có `base.html` với template inheritance. Hãy:
- [ ] Review lại cấu trúc blocks trong base.html
- [ ] Tạo thêm block mới cho metadata (meta description, keywords)
- [ ] Cải thiện sidebar blocks

#### 2. Template Tags & Filters
- [ ] Thêm filters tùy chỉnh vào templates
- [ ] Sử dụng more advanced tags (regroup, lorem, etc.)
- [ ] Format dates theo chuẩn Việt Nam
- [ ] Format currency theo chuẩn VND

#### 3. Static Files Management
- [ ] Review cấu hình static files
- [ ] Tổ chức lại CSS files
- [ ] Tối ưu JavaScript files
- [ ] Thêm custom CSS components

### Afternoon (4h) 🌆

#### 4. Context Processors ✨ NEW
- [ ] Tạo custom context processor cho site settings
- [ ] Tạo context processor cho cart count
- [ ] Tạo context processor cho latest products
- [ ] Thêm vào settings.py

#### 5. Custom Template Tags ✨ NEW
- [ ] Tạo thư mục templatetags
- [ ] Tạo custom filters (format_price, in_stock, etc.)
- [ ] Tạo simple tags (current_year, etc.)
- [ ] Tạo inclusion tags (product_card, etc.)

#### 6. Media Files Handling
- [ ] Review cấu hình media files
- [ ] Thêm validation cho image uploads
- [ ] Tạo thumbnails cho products
- [ ] Hiển thị images với lazy loading

#### 7. Frontend Integration
- [ ] Cải thiện AJAX calls
- [ ] Thêm loading states
- [ ] Thêm animations
- [ ] Improve UX/UI

## 🛠️ Cấu Trúc Project Hiện Tại

```
Day4/Exercise/
├── ecommerce_project/
│   └── settings.py          # Configuration
├── store/
│   ├── models.py            # Database models
│   ├── views.py             # View functions
│   ├── views_api.py         # API endpoints
│   ├── urls.py              # URL patterns
│   ├── urls_api.py          # API URLs
│   ├── templates/store/     # HTML templates
│   ├── static/store/        # Static files (CSS, JS)
│   ├── media/               # Media files (images)
│   └── management/commands/ # Management commands
└── docker-compose.yml       # Docker setup
```

## 📝 Checklist Implementation

### Bài 1: Template Inheritance (30 phút)
- [ ] Review base.html structure
- [ ] Add new blocks (meta, extra_head, extra_js)
- [ ] Improve child templates

### Bài 2: Tags & Filters (1 giờ)
- [ ] Review existing filters usage
- [ ] Add date formatting filters
- [ ] Add currency formatting
- [ ] Add truncate filters

### Bài 3: Static Files (1 giờ)
- [ ] Review static files setup
- [ ] Organize CSS files
- [ ] Optimize JavaScript
- [ ] Add custom components

### Bài 4: Context Processors (1.5 giờ) ✨
- [ ] Create `store/context_processors.py`
- [ ] Add site_settings processor
- [ ] Add cart_count processor
- [ ] Add latest_products processor
- [ ] Update settings.py
- [ ] Use in templates

### Bài 5: Custom Template Tags (2 giờ) ✨
- [ ] Create `store/templatetags/` directory
- [ ] Create `store_filters.py`
- [ ] Create custom filters (price, stock, etc.)
- [ ] Create simple tags
- [ ] Create inclusion tags
- [ ] Test in templates

### Bài 6: Media Files (1 giờ)
- [ ] Review media configuration
- [ ] Add image validation
- [ ] Create thumbnails
- [ ] Add lazy loading

### Bài 7: Frontend (1 giờ)
- [ ] Improve AJAX calls
- [ ] Add loading states
- [ ] Add animations
- [ ] Improve UX

## 🚀 Bắt Đầu

### Step 1: Start Project
```bash
cd /Users/user/Desktop/python-django/Day4/Exercise
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py seed_store --categories 20 --products 2000
```

### Step 2: Review Structure
- Review `store/templates/store/base.html`
- Review `store/models.py`
- Review `store/views.py`

### Step 3: Implement Day 4 Tasks
- Start with Context Processors (Bài 4)
- Then Custom Template Tags (Bài 5)
- Then improve existing features

## 📚 Tài Liệu Tham Khảo

Xem trong thư mục `Learn/`:
- `01_TEMPLATE_INHERITANCE.md` - Template inheritance
- `02_TEMPLATE_TAGS_FILTERS.md` - Tags & filters
- `03_STATIC_FILES.md` - Static files
- `04_CONTEXT_PROCESSORS.md` - Context processors ⭐
- `05_CUSTOM_TEMPLATE_TAGS.md` - Custom tags ⭐
- `06_MEDIA_FILES.md` - Media files
- `07_FRONTEND_INTEGRATION.md` - Frontend

## ⚡ Quick Tasks

### Task 1: Create Context Processor
```python
# store/context_processors.py
def site_settings(request):
    return {
        'site_name': 'TechStore 2025',
        'current_year': 2024,
    }
```

### Task 2: Create Custom Filters
```python
# store/templatetags/store_filters.py
from django import template
register = template.Library()

@register.filter
def format_vnd(amount):
    return f"{int(amount):,} đ"
```

### Task 3: Use in Template
```django
{% load store_filters %}
{{ product.price|format_vnd }}
```

## ✅ Completion Checklist

Khi hoàn thành, bạn sẽ có:
- [x] Working project với template inheritance
- [ ] Custom context processors
- [ ] Custom template tags
- [ ] Improved static files organization
- [ ] Better media handling
- [ ] Enhanced frontend experience

---

**Ready to learn! Let's improve this project! 🚀**
