# Django ORM Fundamentals

## What is ORM?

**ORM** (Object-Relational Mapping) is a technique that lets you interact with your database using Python objects instead of SQL queries.

### Benefits of Django ORM

- **Database Independent**: Works with PostgreSQL, MySQL, SQLite, etc.
- **Type Safe**: Python classes instead of string SQL
- **Security**: Automatic SQL injection protection
- **Efficiency**: Less boilerplate code
- **Migrations**: Automatic database schema management

## Basic Concepts

## Model = Table

```python
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
  
    def __str__(self):
        return self.name
```

**Becomes**:

```sql
CREATE TABLE ecommerce_product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    description TEXT NOT NULL
);
```

### Objects = Query Interface

```python
# Django ORM
products = Product.objects.all()

# Equivalent SQL
# SELECT * FROM ecommerce_product;
```

## Django ORM vs Raw SQL

### Raw SQL

```python
from django.db import connection

def get_products_raw():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM ecommerce_product")
        return cursor.fetchall()
```

### Django ORM

```python
def get_products_orm():
    return Product.objects.all()
```

**ORM is cleaner and safer!**

## Model Definition

### Basic Model

```python
from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    published_date = models.DateField()
    isbn = models.CharField(max_length=13, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
  
    class Meta:
        db_table = 'books'
        ordering = ['-published_date']
```

### Common Field Types

```python
class MyModel(models.Model):
    # Text Fields
    name = models.CharField(max_length=100)
    description = models.TextField()
  
    # Numbers
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField()
  
    # Boolean
    is_active = models.BooleanField(default=True)
  
    # Date/Time
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
  
    # Choice Fields
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
  
    # Slug
    slug = models.SlugField(unique=True)
  
    # File Upload
    image = models.ImageField(upload_to='images/')
  
    # URLs
    website = models.URLField()
```

## Field Options

### Common Options

```python
class Product(models.Model):
    # Required field
    name = models.CharField(max_length=200)
  
    # Optional field
    description = models.TextField(blank=True, null=True)
  
    # Default value
    is_active = models.BooleanField(default=True)
  
    # Unique constraint
    sku = models.CharField(max_length=50, unique=True)
  
    # Database column name
    published = models.BooleanField(db_column='is_published')
  
    # Help text (for admin)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Price in USD"
    )
  
    # Validators
    email = models.EmailField(validators=[validate_email])
```

## Relationships

### ForeignKey (Many-to-One)

```python
class Category(models.Model):
    name = models.CharField(max_length=100)

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
```

**Relationship**: Many Products belong to One Category

### ManyToManyField (Many-to-Many)

```python
class Tag(models.Model):
    name = models.CharField(max_length=50)

class Product(models.Model):
    name = models.CharField(max_length=200)
    tags = models.ManyToManyField(Tag)
```

**Relationship**: Products can have Many Tags, Tags can be on Many Products

### OneToOneField (One-to-One)

```python
class Product(models.Model):
    name = models.CharField(max_length=200)

class ProductDetail(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    long_description = models.TextField()
```

**Relationship**: One Product has One ProductDetail

## On Delete Behaviors

```python
# CASCADE: Delete related objects
category = models.ForeignKey(Category, on_delete=models.CASCADE)

# PROTECT: Prevent deletion
category = models.ForeignKey(Category, on_delete=models.PROTECT)

# SET_NULL: Set to NULL
category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

# SET_DEFAULT: Set to default
category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default=1)

# DO_NOTHING: Leave as is
category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
```

## Best Practices

### 1. Always use `__str__`

```python
def __str__(self):
    return self.name
```

### 2. Use verbose names

```python
class Product(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Product Name",
        help_text="Enter the product name"
    )
```

### 3. Set appropriate defaults

```python
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
is_active = models.BooleanField(default=True)
```

### 4. Use Meta class

```python
class Meta:
    db_table = 'products'  # Custom table name
    ordering = ['-created_at']  # Default ordering
    verbose_name = 'Product'  # Singular name
    verbose_name_plural = 'Products'  # Plural name
```

## Model Methods

### Instance Methods

```python
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.IntegerField(default=0)
  
    def __str__(self):
        return self.name
  
    def get_discounted_price(self):
        """Calculate price after discount"""
        return self.price * (1 - self.discount_percent / 100)
  
    def is_on_sale(self):
        """Check if product is on sale"""
        return self.discount_percent > 0
  
    def save(self, *args, **kwargs):
        """Override save method"""
        # Do something before saving
        if self.price < 0:
            raise ValueError("Price cannot be negative")
        super().save(*args, **kwargs)
```

## Summary

- **Model** = Python class representing database table
- **Field** = Attribute representing database column
- **Relationships** = Connect models together
- **On_delete** = What happens when related object is deleted
- **__str__** = Human-readable representation
- **Meta** = Model metadata and options
- **Methods** = Add business logic to models
