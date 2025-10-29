# Media Files Handling

## 📖 Khái Niệm

Media files là các file được upload bởi users như:
- Images (photos, avatars)
- Documents (PDFs, Word files)
- Videos
- Audio files

## ⚙️ Cấu Hình

### Settings.py

```python
# settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Tạo thư mục media nếu chưa có
if not os.path.exists(MEDIA_ROOT):
    os.makedirs(MEDIA_ROOT)
```

### URL Configuration

```python
# urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## 📁 Cấu Trúc Thư Mục

```
project/
├── media/
│   ├── avatars/
│   │   └── user_123.jpg
│   ├── products/
│   │   └── laptop_001.jpg
│   ├── documents/
│   │   └── report.pdf
│   └── uploads/
└── myapp/
```

## 💾 Model Fields

### ImageField

```python
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text="User avatar image"
    )
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(
        upload_to='products/%Y/%m/',
        blank=True,
        help_text="Product main image"
    )
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    featured_image = models.ImageField(
        upload_to='blog/%Y/%m/%d/',
        blank=True
    )
    created = models.DateTimeField(auto_now_add=True)
```

### FileField

```python
class Document(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(
        upload_to='documents/%Y/%m/',
        help_text="PDF or document file"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def file_size(self):
        """Return file size in MB"""
        if self.file:
            return round(self.file.size / 1024 / 1024, 2)
        return 0
```

## 📝 Forms with File Upload

### ModelForm

```python
# forms.py
from django import forms
from .models import UserProfile, Product, Document

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'avatar': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control'
            }),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'accept': 'image/*'}),
        }

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={
                'accept': '.pdf,.doc,.docx',
                'class': 'form-control'
            }),
        }
```

## 🎨 Templates

### Display Image

```django
{# templates/product_detail.html #}
{% load static %}

<div class="product">
    {% if product.image %}
        <img src="{{ product.image.url }}" alt="{{ product.name }}">
    {% else %}
        <img src="{% static 'images/placeholder.jpg' %}" alt="No image">
    {% endif %}
    
    <h3>{{ product.name }}</h3>
    <p class="price">${{ product.price }}</p>
</div>
```

### Form with Upload

```django
{# templates/profile_edit.html #}
{% load static %}
{% load crispy_forms_tags %}

<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    
    {% if form.avatar.value %}
        <div class="current-avatar">
            <img src="{{ form.avatar.value.url }}" alt="Current avatar">
            <p>Current Avatar</p>
        </div>
    {% endif %}
    
    {{ form.as_p }}
    
    <button type="submit" class="btn btn-primary">Update Profile</button>
</form>
```

### Image Gallery

```django
{# templates/products.html #}
<div class="product-grid">
    {% for product in products %}
        <div class="product-card">
            <a href="{% url 'product_detail' product.id %}">
                {% if product.image %}
                    <img src="{{ product.image.url }}" 
                         alt="{{ product.name }}"
                         loading="lazy">
                {% else %}
                    <img src="{% static 'images/no-image.jpg' %}" 
                         alt="No image">
                {% endif %}
            </a>
            <h3>{{ product.name }}</h3>
            <p class="price">${{ product.price }}</p>
        </div>
    {% endfor %}
</div>
```

## ⚙️ Views

### Upload View

```python
# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserProfileForm, ProductForm

@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'profile_edit.html', {'form': form})

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('product_detail', pk=product.id)
    else:
        form = ProductForm()
    
    return render(request, 'product_add.html', {'form': form})
```

### Display with Thumbnails

```python
# utils.py
from PIL import Image
import os

def create_thumbnail(image_path, size=(200, 200)):
    """Create thumbnail from image"""
    img = Image.open(image_path)
    img.thumbnail(size, Image.LANCZOS)
    
    # Get directory and filename
    directory = os.path.dirname(image_path)
    filename = os.path.basename(image_path)
    name, ext = os.path.splitext(filename)
    
    # Save thumbnail
    thumb_path = os.path.join(directory, f"{name}_thumb{ext}")
    img.save(thumb_path)
    
    return thumb_path

# In views or models
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from PIL import Image

class Product(models.Model):
    # ... fields ...
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Create thumbnail after save
        if self.image:
            img = Image.open(self.image.path)
            
            if img.height > 300 or img.width > 300:
                img.thumbnail((300, 300), Image.LANCZOS)
                img.save(self.image.path)
```

## 🎯 Advanced Examples

### Multiple Image Upload

```python
# models.py
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/images/')
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.product.name} - Image"

# forms.py
class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={'multiple': True}),
        }

# views.py
def upload_product_images(request, product_id):
    product = Product.objects.get(id=product_id)
    
    if request.method == 'POST':
        images = request.FILES.getlist('images')
        
        for img in images:
            ProductImage.objects.create(
                product=product,
                image=img,
                is_primary=False
            )
        
        messages.success(request, f'{len(images)} images uploaded!')
        return redirect('product_detail', pk=product_id)
    
    return render(request, 'upload_images.html', {'product': product})
```

### File Download

```python
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, FileResponse
import os

def download_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    
    # Option 1: Serve file directly
    response = FileResponse(
        open(document.file.path, 'rb'),
        content_type='application/octet-stream'
    )
    response['Content-Disposition'] = f'attachment; filename="{document.title}.pdf"'
    return response
    
    # Option 2: Return file response
    return FileResponse(document.file.open(), as_attachment=True, filename=f"{document.title}.pdf")
```

## 🔒 Security Considerations

### File Validation

```python
# validators.py
from django.core.exceptions import ValidationError
import os

def validate_image_size(image):
    """Validate image size"""
    if image.size > 5 * 1024 * 1024:  # 5MB
        raise ValidationError("Image size cannot exceed 5MB")

def validate_file_extension(file):
    """Validate file extension"""
    ext = os.path.splitext(file.name)[1]
    valid_extensions = ['.pdf', '.doc', '.docx']
    if ext.lower() not in valid_extensions:
        raise ValidationError("Unsupported file format")

# In models
from .validators import validate_image_size, validate_file_extension

class Product(models.Model):
    image = models.ImageField(
        upload_to='products/',
        validators=[validate_image_size]
    )

class Document(models.Model):
    file = models.FileField(
        upload_to='documents/',
        validators=[validate_file_extension]
    )
```

## ✅ Checklist

- [ ] Cấu hình MEDIA_URL và MEDIA_ROOT
- [ ] Thêm static() vào urls.py
- [ ] Tạo model với ImageField/FileField
- [ ] Tạo form với file upload
- [ ] Xử lý trong view
- [ ] Hiển thị trong template
- [ ] Validate file types và sizes
- [ ] Handle missing images
