# 🎓 Day 4 - Django Template Language

## 📚 Tổng Quan

Day 4 tập trung vào việc học Django Template Language (DTL) và các kỹ thuật xử lý frontend trong Django.

## 📖 Nội Dung Học

### Morning (4h) 🌅

#### 1. [Template Inheritance](./01_TEMPLATE_INHERITANCE.md)
- Khái niệm và cú pháp
- Sử dụng `{% extends %}` và `{% block %}`
- Template cha và template con
- Sử dụng `{{ block.super }}`
- Ví dụ thực tế: website e-commerce, blog

#### 2. [Template Tags & Filters](./02_TEMPLATE_TAGS_FILTERS.md)
- If/Else tags
- For loop với forloop variables
- URL tags với parameters
- Static files tags
- Built-in filters (string, date, number)
- Ví dụ: product list, blog posts, user profiles

#### 3. [Static Files Management](./03_STATIC_FILES.md)
- Cấu hình STATIC_URL và STATIC_ROOT
- Cấu hình MEDIA_URL và MEDIA_ROOT
- Cấu trúc thư mục static files
- Sử dụng trong templates
- CSS và JavaScript files
- Production với collectstatic

### Afternoon (4h) 🌆

#### 4. [Context Processors](./04_CONTEXT_PROCESSORS.md)
- Khái niệm context processors
- Built-in context processors
- Tạo custom context processor
- Ví dụ: site settings, navigation, user data
- Best practices

#### 5. [Custom Template Tags](./05_CUSTOM_TEMPLATE_TAGS.md)
- Tạo custom filters
- Tạo custom template tags (simple tags)
- Tạo inclusion tags
- Ví dụ: e-commerce filters, blog tags, utilities
- Advanced examples

#### 6. [Media Files Handling](./06_MEDIA_FILES.md)
- ImageField và FileField
- Forms với file upload
- Display images trong templates
- File validation
- Advanced: multiple images, thumbnails
- Security considerations

#### 7. [Frontend Integration](./07_FRONTEND_INTEGRATION.md)
- Tích hợp Bootstrap 5
- Tích hợp Tailwind CSS
- JavaScript với Fetch API
- AJAX form submission
- Search functionality
- Complete examples

## 🎯 Mục Tiêu Học Tập

Sau khi hoàn thành Day 4, bạn sẽ:

- ✅ Hiểu và sử dụng template inheritance
- ✅ Áp dụng template tags và filters
- ✅ Quản lý static files
- ✅ Tạo custom context processors
- ✅ Tạo custom template tags
- ✅ Xử lý media files (upload/display)
- ✅ Tích hợp CSS frameworks
- ✅ Tích hợp JavaScript với AJAX
- ✅ Tạo responsive UI

## 📝 Cấu Trúc Files

```
Day4/
├── Learn/
│   ├── README.md (này)
│   ├── 00_DJANGO_TEMPLATE_LANGUAGE.md (Tổng quan)
│   ├── 01_TEMPLATE_INHERITANCE.md
│   ├── 02_TEMPLATE_TAGS_FILTERS.md
│   ├── 03_STATIC_FILES.md
│   ├── 04_CONTEXT_PROCESSORS.md
│   ├── 05_CUSTOM_TEMPLATE_TAGS.md
│   ├── 06_MEDIA_FILES.md
│   └── 07_FRONTEND_INTEGRATION.md
└── Exercise/ (sẽ tạo bài tập thực hành)
```

## 🚀 Bắt Đầu Học

### Thứ Tự Đọc Khuyến Nghị

1. **Đọc tổng quan:** [00_DJANGO_TEMPLATE_LANGUAGE.md](./00_DJANGO_TEMPLATE_LANGUAGE.md)
2. **Học Morning (4h):**
   - [Template Inheritance](./01_TEMPLATE_INHERITANCE.md)
   - [Template Tags & Filters](./02_TEMPLATE_TAGS_FILTERS.md)
   - [Static Files](./03_STATIC_FILES.md)
3. **Học Afternoon (4h):**
   - [Context Processors](./04_CONTEXT_PROCESSORS.md)
   - [Custom Template Tags](./05_CUSTOM_TEMPLATE_TAGS.md)
   - [Media Files](./06_MEDIA_FILES.md)
   - [Frontend Integration](./07_FRONTEND_INTEGRATION.md)

## 💡 Tips Học Tập

1. **Đọc code mẫu:** Mỗi file đều có ví dụ thực tế
2. **Thực hành:** Tạo project nhỏ để test
3. **Copy code:** Sao chép và chạy thử các ví dụ
4. **Sửa đổi:** Thử sửa code để hiểu rõ hơn
5. **Làm bài tập:** Check checklist ở cuối mỗi file

## ✅ Checklist Tổng Quan

### Template Inheritance
- [ ] Hiểu khái niệm inheritance
- [ ] Sử dụng `{% extends %}`
- [ ] Sử dụng `{% block %}`
- [ ] Tạo base template
- [ ] Tạo child templates

### Tags & Filters
- [ ] Sử dụng If/Else tags
- [ ] Sử dụng For loop
- [ ] Sử dụng URL tags
- [ ] Áp dụng filters
- [ ] Format dates, numbers

### Static Files
- [ ] Cấu hình settings
- [ ] Cấu trúc thư mục
- [ ] Sử dụng trong templates
- [ ] CSS files
- [ ] JavaScript files

### Context Processors
- [ ] Hiểu built-in processors
- [ ] Tạo custom processor
- [ ] Sử dụng trong templates

### Custom Tags
- [ ] Tạo custom filters
- [ ] Tạo simple tags
- [ ] Tạo inclusion tags

### Media Files
- [ ] Cấu hình media
- [ ] Upload files
- [ ] Display images
- [ ] Validate files

### Frontend
- [ ] Tích hợp Bootstrap/Tailwind
- [ ] AJAX với JavaScript
- [ ] Form submission
- [ ] Search functionality

## 🔗 Tài Liệu Tham Khảo

- [Django Template Documentation](https://docs.djangoproject.com/en/4.2/ref/templates/)
- [Built-in Tags](https://docs.djangoproject.com/en/4.2/ref/templates/builtins/#built-in-tag-reference)
- [Built-in Filters](https://docs.djangoproject.com/en/4.2/ref/templates/builtins/#built-in-filter-reference)
- [Static Files](https://docs.djangoproject.com/en/4.2/howto/static-files/)
- [File Upload](https://docs.djangoproject.com/en/4.2/topics/http/file-uploads/)

## 📞 Hỗ Trợ

Nếu có thắc mắc, vui lòng:
1. Đọc lại documentation
2. Xem ví dụ code trong các files
3. Tìm kiếm trên Google
4. Hỏi mentor/giảng viên

---

**Happy Learning! 🚀**
