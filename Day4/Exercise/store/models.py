from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from PIL import Image
import os


class Category(models.Model):
    """Product Category Model"""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class Tag(models.Model):
    """Product Tags"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Product Model"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('out_of_stock', 'Out of Stock'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Original price for showing discount"
    )
    
    # Inventory
    stock = models.IntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True)
    
    # Relations
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_featured']),
            models.Index(fields=['category', 'status']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})
    
    @property
    def is_in_stock(self):
        return self.stock > 0
    
    @property
    def discount_percent(self):
        if self.compare_price and self.compare_price > self.price:
            return int((self.compare_price - self.price) / self.compare_price * 100)
        return 0
    
    @property
    def thumbnail_url(self):
        """Return URL to a generated thumbnail, create if missing."""
        if not self.image:
            return ''
        try:
            original_path = self.image.path
            base, ext = os.path.splitext(original_path)
            thumb_path = f"{base}_thumb{ext}"
            # Create thumbnail if it doesn't exist
            if not os.path.exists(thumb_path):
                img = Image.open(original_path)
                img.thumbnail((400, 400), Image.LANCZOS)
                img.save(thumb_path)
            # Build URL
            rel_thumb = os.path.relpath(thumb_path, settings.MEDIA_ROOT)
            return f"{settings.MEDIA_URL}{rel_thumb}".replace('\\', '/')
        except Exception:
            # Fallback to original image URL
            return self.image.url if self.image else ''
    
    def save(self, *args, **kwargs):
        if not self.sku:
            # Generate unique SKU based on name and timestamp
            import time
            timestamp = int(time.time())
            name_part = self.name.replace(' ', '').upper()[:8]
            self.sku = f"{name_part}-{timestamp}"
        super().save(*args, **kwargs)


class Customer(models.Model):
    """Customer Model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='customer_profile')
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='USA')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Order(models.Model):
    """Order Model"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Shipping address (can be different from customer address)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100)
    
    # Timestamps
    order_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-order_date']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['status', 'order_date']),
        ]
    
    def __str__(self):
        return f"Order #{self.order_number}"
    
    def calculate_total(self):
        """Calculate total amount from order items"""
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        self.save()
        return total


class OrderItem(models.Model):
    """Order Item Model - Links Order and Product"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ['order', 'product']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    @property
    def subtotal(self):
        return self.price * self.quantity


class Cart(models.Model):
    """Cart Model - Stores user's shopping cart"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['customer', 'product']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer.name} - {self.product.name} ({self.quantity})"


class Subscriber(models.Model):
    """Newsletter subscribers."""
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.email

class EmailOTP(models.Model):
    """Email-based one-time password for registration/verification."""
    email = models.EmailField(db_index=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['email', 'is_used']),
        ]

    def __str__(self):
        return f"OTP for {self.email} ({'used' if self.is_used else 'active'})"


class PromoCode(models.Model):
    """Promo code issuance and usage tracking."""
    promo_code = models.CharField(max_length=64, unique=True, db_index=True)
    is_used = models.BooleanField(default=False)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='promo_codes')
    promo_amount = models.PositiveSmallIntegerField(default=10, help_text='Discount percent (e.g., 10 means 10%)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['promo_code', 'is_used']),
            models.Index(fields=['user', 'is_used']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.promo_code} ({'used' if self.is_used else 'unused'})"
