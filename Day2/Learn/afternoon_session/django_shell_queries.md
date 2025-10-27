# Working with Django Shell and Queries

## Django Shell

Django shell is an interactive Python shell with Django context.

### Starting Django Shell

```bash
python manage.py shell
```

### Better Shell: iPython

```bash
pip install ipython
python manage.py shell
# OR
python manage.py shell_plus  # With django-extensions
```

## Basic Queries

### Get All Objects

```python
# Get all products
from ecommerce.models import Product

products = Product.objects.all()
print(products)  # <QuerySet [<Product>, <Product>]>
```

### Get Single Object

```python
# By primary key
product = Product.objects.get(pk=1)

# By field
product = Product.objects.get(name="Laptop")

# Get or 404 (for views)
from django.shortcuts import get_object_or_404
product = get_object_or_404(Product, pk=1)
```

### Filter Objects

```python
# Filter by field
laptops = Product.objects.filter(category__name="Laptop")

# Multiple filters
cheap_laptops = Product.objects.filter(
    category__name="Laptop",
    price__lt=1000
)

# Exclude
inactive_products = Product.objects.exclude(is_active=True)
```

## Field Lookups

### Basic Lookups

```python
# Exact match
Product.objects.filter(name="Laptop")

# Case-insensitive
Product.objects.filter(name__iexact="laptop")

# Contains
Product.objects.filter(name__contains="laptop")

# Starts with / Ends with
Product.objects.filter(name__startswith="Lap")
Product.objects.filter(name__endswith="top")

# Case-insensitive versions
Product.objects.filter(name__icontains="lap")
```

### Number Lookups

```python
# Greater than / Less than
Product.objects.filter(price__gt=100)
Product.objects.filter(price__gte=100)  # Greater or equal
Product.objects.filter(price__lt=1000)   # Less than
Product.objects.filter(price__lte=1000) # Less or equal

# Range
Product.objects.filter(price__range=(50, 200))
```

### Date Lookups

```python
from django.utils import timezone
from datetime import datetime, timedelta

# Today
Product.objects.filter(created_at__date=timezone.now().date())

# This month
Product.objects.filter(created_at__month=timezone.now().month)

# Last 7 days
week_ago = timezone.now() - timedelta(days=7)
Product.objects.filter(created_at__gte=week_ago)

# Year, month, day
Product.objects.filter(created_at__year=2025)
Product.objects.filter(created_at__month=10)
Product.objects.filter(created_at__day=27)
```

### Null/Blank Lookups

```python
Product.objects.filter(description__isnull=True)
Product.objects.exclude(description__isnull=True)
```

## Ordering

```python
# Order by
products = Product.objects.all().order_by('price')
products = Product.objects.all().order_by('-price')  # Descending
products = Product.objects.all().order_by('name', '-price')

# Random
from django.db.models import Count
products = Product.objects.all().order_by('?')

# Meta ordering (in model)
class Product(models.Model):
    class Meta:
        ordering = ['-created_at']
```

## Chaining Queries

```python
# All chaining operations return QuerySet
products = Product.objects \
    .filter(is_active=True) \
    .exclude(price__lt=10) \
    .order_by('-created_at')

# Only executed when evaluated
print(products)  # Now executes query
```

## QuerySet Methods

### Count

```python
total = Product.objects.count()
active_products = Product.objects.filter(is_active=True).count()
```

### Exists

```python
if Product.objects.filter(name="Laptop").exists():
    print("Laptop exists!")
```

### Latest / Earliest

```python
latest_product = Product.objects.latest('created_at')
oldest_product = Product.objects.earliest('created_at')
```

### First / Last

```python
first_product = Product.objects.first()
last_product = Product.objects.last()
```

### Create / Update / Delete

```python
# Create
product = Product.objects.create(
    name="Mouse",
    price=29.99,
    description="Wireless mouse"
)

# Update
Product.objects.filter(name="Mouse").update(price=24.99)

# Delete
Product.objects.filter(name="Mouse").delete()
```

## Advanced Queries

### Q Objects

```python
from django.db.models import Q

# OR
products = Product.objects.filter(
    Q(name__contains="Laptop") | Q(name__contains="Keyboard")
)

# AND
products = Product.objects.filter(
    Q(price__gte=100) & Q(price__lte=1000)
)

# NOT
products = Product.objects.filter(~Q(is_active=True))
```

### Aggregation

```python
from django.db.models import Avg, Max, Min, Sum, Count

# Average
avg_price = Product.objects.aggregate(Avg('price'))

# Multiple aggregations
stats = Product.objects.aggregate(
    avg_price=Avg('price'),
    max_price=Max('price'),
    min_price=Min('price'),
    total=Sum('price'),
    count=Count('id')
)

# Group by
from django.db.models import Count
products_by_category = Product.objects.values('category').annotate(
    total=Count('id'),
    avg_price=Avg('price')
)
```

### Annotation

```python
from django.db.models import F, Value, Count

# Create computed fields
products = Product.objects.annotate(
    discounted_price=F('price') * 0.9
)

# Add constants
products = Product.objects.annotate(
    currency=Value('USD')
)

# Count related objects
categories = Category.objects.annotate(
    product_count=Count('product')
)
```

## Relationship Queries

### ForeignKey (Many-to-One)

```python
# Get all products in a category
category = Category.objects.get(name="Electronics")
products = category.product_set.all()  # Reverse lookup

# Filter by related field
products = Product.objects.filter(category__name="Electronics")

# Follow relationships
products = Product.objects.filter(
    category__parent__name="Technology"
)
```

### ManyToMany

```python
# Get tags for a product
product = Product.objects.get(name="Laptop")
tags = product.tags.all()

# Get products for a tag
tag = Tag.objects.get(name="Sale")
products = tag.product_set.all()

# Filter by many-to-many field
products = Product.objects.filter(tags__name="Sale")
```

### Reverse Relationships

```python
# ForeignKey reverse
category.product_set.all()
category.product_set.filter(name="Laptop")

# Many-to-many reverse
tag.product_set.all()
tag.product_set.count()

# Access from both sides
product.category.name
category.product_set.first()
```

## Query Optimization

### Avoid N+1 Queries

```python
# BAD - N+1 queries
products = Product.objects.all()
for product in products:
    print(product.category.name)  # Query for each product!

# GOOD - Select related
products = Product.objects.select_related('category')
for product in products:
    print(product.category.name)  # No extra queries!
```

### select_related (ForeignKey, OneToOne)

```python
# Fetch related ForeignKey in one query
products = Product.objects.select_related('category')
```

### prefetch_related (ManyToMany, Reverse ForeignKey)

```python
# Fetch ManyToMany in separate optimized query
products = Product.objects.prefetch_related('tags')
```

### Combined

```python
# Both together
products = Product.objects.select_related('category').prefetch_related('tags')
```

## Using `only()` and `defer()`

```python
# Only fetch specific fields
products = Product.objects.only('name', 'price')

# Exclude specific fields
products = Product.objects.defer('description')
```

## Debugging Queries

### Print SQL

```python
products = Product.objects.all()
print(products.query)  # Print SQL
```

### Enable Debugging

```python
from django.db import connection

# ... your queries ...

print(len(connection.queries))  # Number of queries
for query in connection.queries:
    print(query['sql'])
```

## Real-World Examples

```python
# Most expensive product in each category
from django.db.models import Max

categories = Category.objects.annotate(
    max_price=Max('product__price')
)

# Products with discounts
products = Product.objects.annotate(
    savings=F('price') - F('discounted_price')
).filter(savings__gt=0)

# Recent orders for products
products = Product.objects.prefetch_related(
    'orderitem_set__order'
).filter(orderitem_set__order__created_at__gte=yesterday)
```

## Summary

- **QuerySets are lazy**: Only execute when evaluated
- **Use select_related**: For ForeignKey relationships
- **Use prefetch_related**: For ManyToMany relationships
- **Chain methods**: Most QuerySet methods return QuerySets
- **Use Q objects**: For complex OR/AND queries
- **Aggregate data**: Use annotate() and aggregate()
- **Debug queries**: Print query to see SQL

