# Database Migrations in Django

## What are Migrations?

**Migrations** are Django's way of propagating changes to your models into the database schema. They're version control for your database.

## Why Migrations?

- Track database schema changes
- Version control your database
- Apply changes incrementally
- Rollback database changes
- Keep databases in sync across environments

## Migration Workflow

### 1. Create Migration

```bash
python manage.py makemigrations
```

This creates migration files based on model changes.

### 2. Apply Migration

```bash
python manage.py migrate
```

This applies migrations to the database.

### 3. Check Status

```bash
python manage.py showmigrations
```

Shows which migrations are applied.

## Creating Migrations

### Automatic Migration Creation

```python
# models.py
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
```

```bash
python manage.py makemigrations
# Migrations for 'ecommerce':
#   ecommerce/migrations/0001_initial.py
#     - Create model Product
```

### Specific App Migration

```bash
python manage.py makemigrations ecommerce
```

### Check SQL Before Migrating

```bash
python manage.py sqlmigrate ecommerce 0001
```

Shows the SQL that will be executed.

## Migration Files

### Structure

```python
# ecommerce/migrations/0001_initial.py
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    
    dependencies = [
        # Other migrations this depends on
    ]
    
    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(...)),
                ('name', models.CharField(max_length=200)),
                ('price', models.DecimalField(...)),
            ],
        ),
    ]
```

### Operations

```python
# Create model
migrations.CreateModel(...)

# Add field
migrations.AddField(...)

# Remove field
migrations.RemoveField(...)

# Rename field
migrations.RenameField(...)

# Create index
migrations.CreateIndex(...)

# Alter model
migrations.AlterModelOptions(...)
```

## Adding Fields

### Step 1: Modify Model

```python
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # NEW FIELD
    description = models.TextField(blank=True)
```

### Step 2: Create Migration

```bash
python manage.py makemigrations
```

### Step 3: Apply Migration

```bash
python manage.py migrate
```

## Field Modifications

### Adding NOT NULL Field

**Problem**: Adding a NOT NULL field to existing data

```python
# WRONG
category = models.ForeignKey(Category, on_delete=models.CASCADE)
# Error: NOT NULL constraint

# CORRECT
category = models.ForeignKey(
    Category, 
    on_delete=models.CASCADE,
    null=True,  # Allow NULL temporarily
    default=None
)
```

Then provide default, then remove null=True

```python
# Step 1: Add with default
category = models.ForeignKey(
    Category, 
    on_delete=models.CASCADE,
    null=True,
    default=1  # Set default to existing category
)

# Step 2: Create and apply migration

# Step 3: Remove null
category = models.ForeignKey(Category, on_delete=models.CASCADE)
```

## Data Migrations

### Run Python Code During Migration

```python
# ecommerce/migrations/0002_populate_category.py
from django.db import migrations

def populate_categories(apps, schema_editor):
    Category = apps.get_model('ecommerce', 'Category')
    Category.objects.create(name='Electronics')
    Category.objects.create(name='Clothing')

class Migration(migrations.Migration):
    dependencies = [
        ('ecommerce', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(populate_categories),
    ]
```

## Advanced Migrations

### Rename Model

```python
# Step 1: Rename in code
class Product(models.Model):
    ...

# Step 2: Create migration
python manage.py makemigrations ecommerce --name rename_product

# Edit migration file
class Migration(migrations.Migration):
    operations = [
        migrations.RenameModel('Product', 'Item'),
    ]
```

### Custom Migration

```python
# ecommerce/migrations/0003_custom_migration.py
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('ecommerce', '0002_previous'),
    ]
    
    operations = [
        migrations.RunSQL(
            "ALTER TABLE ecommerce_product RENAME TO product_new;"
        ),
    ]
```

## Common Commands

### View Migrations

```bash
# Show all migrations
python manage.py showmigrations

# Show specific app
python manage.py showmigrations ecommerce

# Show unapplied
python manage.py showmigrations ecommerce | grep "\[ \]"
```

### Rollback Migrations

```bash
# Rollback to specific migration
python manage.py migrate ecommerce 0001

# Rollback all
python manage.py migrate ecommerce zero
```

### Fake Migrations

```bash
# Mark migration as applied without running it
python manage.py migrate --fake ecommerce 0002
```

## Common Issues

### 1. Migration Conflicts

**Problem**: Different models with same migration number

**Solution**: Merge migrations

```bash
python manage.py makemigrations --merge
```

### 2. No Changes Detected

**Problem**: Changed model but no migration created

**Solution**: 

```bash
# Force migration creation
python manage.py makemigrations --name custom_name

# Or check if model is in INSTALLED_APPS
```

### 3. Migration Already Applied

**Problem**: Migration applied but model doesn't exist

**Solution**: Reset migrations

```bash
# Delete migration files (keep __init__.py)
# Delete database tables
python manage.py migrate
```

## Best Practices

### 1. Always Test Migrations

```bash
# Test on staging first
# Always backup database before migration
```

### 2. Commit Migration Files

```bash
# Migration files should be in version control
git add ecommerce/migrations/
git commit -m "Add Product model"
```

### 3. Never Edit Applied Migrations

```bash
# If migration is applied, create new one
# Never edit existing migration files
```

### 4. Use Descriptive Names

```bash
python manage.py makemigrations --name add_product_category
```

### 5. Review SQL

```bash
python manage.py sqlmigrate ecommerce 0002
```

## Summary

- **makemigrations**: Create migration files from model changes
- **migrate**: Apply migrations to database
- **showmigrations**: View migration status
- **sqlmigrate**: View SQL for migration
- Always test migrations
- Commit migration files to version control



