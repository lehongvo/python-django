# Exercise: E-commerce System with Django ORM

## Exercise Overview

Design and implement a complete e-commerce system with Django models for products, categories, orders, and customers.

## Learning Objectives

By completing this exercise, you will:
- Design proper database models for e-commerce
- Implement model relationships (ForeignKey, ManyToMany)
- Create database migrations
- Use Django shell for data operations
- Apply QuerySet optimization
- Build admin interface for e-commerce management

## Exercise Requirements

### Models to Implement

1. **Category**: Product categories
   - name, description, parent category

2. **Product**: Products in inventory
   - name, description, price, stock, category, tags

3. **Customer**: Customer information
   - name, email, phone, address

4. **Order**: Customer orders
   - customer, order date, status, total amount

5. **OrderItem**: Items in an order
   - order, product, quantity, price

### Features

- Full CRUD operations for all models
- Django admin interface
- Model relationships
- QuerySet optimization
- Database migrations

## Estimated Time

**Basic implementation**: 4-6 hours  
**With advanced features**: 6-8 hours

## Deliverables

1. Working e-commerce Django application
2. Complete model definitions with relationships
3. Admin interface configuration
4. Migration files
5. Sample data

## Getting Started

1. Navigate to Exercise folder
2. Run: `docker-compose up`
3. Access: http://localhost:8000
4. Admin: http://localhost:8000/admin

