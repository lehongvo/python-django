# Exercise: Django Blog with CRUD Operations 🚀

## Quick Start with Docker

**⚠️ Prerequisites**: Make sure Docker Desktop is running!

```bash
# Navigate to Exercise directory
cd Day1/Exercise

# Start the application
bash start.sh

# Access at:
# - Blog: http://localhost:8000
# - Admin: http://localhost:8000/admin
# - Username: admin
# - Password: admin123
```

For detailed setup instructions, see [DOCKER_SETUP.md](DOCKER_SETUP.md)

---

## Exercise Overview

Create a simple Django blog application with full CRUD (Create, Read, Update, Delete) operations.

## Learning Objectives

By completing this exercise, you will:
- Set up a Django project and app
- Create database models
- Build views for CRUD operations
- Create HTML templates
- Use Django admin interface
- Understand the MVT pattern in practice

## Exercise Requirements

### Core Features

1. **Models**: Create a BlogPost model with fields:
   - title (CharField)
   - content (TextField)
   - author (CharField)
   - published_date (DateTimeField)
   - is_published (BooleanField)

2. **Views**: Implement CRUD operations:
   - List all posts (Read)
   - View single post detail (Read)
   - Create new post (Create)
   - Edit existing post (Update)
   - Delete post (Delete)

3. **Templates**: Create HTML templates for:
   - Post list page
   - Post detail page
   - Post creation form
   - Post edit form
   - Confirmation page for delete

4. **Admin**: Register BlogPost model in Django admin

## Step-by-Step Instructions

### Part 1: Setup (30 minutes)

1. Create virtual environment
2. Install Django
3. Create Django project
4. Create blog app
5. Configure settings

### Part 2: Models (20 minutes)

1. Define BlogPost model
2. Create and run migrations
3. Register model in admin
4. Create superuser

### Part 3: Views and URLs (40 minutes)

1. Create function-based views
2. Configure URL patterns
3. Test basic routing

### Part 4: Templates (30 minutes)

1. Create base template
2. Create post list template
3. Create post detail template
4. Create form templates

### Part 5: CRUD Implementation (60 minutes)

1. Implement Create operation
2. Implement Read operations
3. Implement Update operation
4. Implement Delete operation
5. Add success messages

## Bonus Features

- Add categories to posts
- Implement search functionality
- Add pagination
- Style with CSS/Bootstrap
- Add image upload feature
- Implement comment system

## Estimated Time

**Basic implementation**: 3-4 hours
**With bonus features**: 5-6 hours

## Getting Started

1. Navigate to Exercise folder
2. Follow the step-by-step instructions in `instructions.md`
3. Use `solution/` folder for reference if stuck
4. Test your implementation thoroughly

## Deliverables

1. Working Django blog application
2. All CRUD operations functional
3. Django admin configured
4. Clean, readable code
5. README with setup instructions

## Assessment Criteria

- [ ] Project setup correctly
- [ ] Models defined and migrated
- [ ] All CRUD views implemented
- [ ] Templates created and styled
- [ ] Admin interface functional
- [ ] Code follows Django best practices
- [ ] No runtime errors
- [ ] Clean project structure

