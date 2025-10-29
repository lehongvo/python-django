# Frontend Integration

## 📖 Khái Niệm

Tích hợp frontend framework (Bootstrap, Tailwind, Vue, React) vào Django templates để tạo UI hiện đại và responsive.

## 🎨 CSS Frameworks

### 1. Bootstrap 5

#### Cài đặt via CDN

```django
{# templates/base.html #}
{% load static %}
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}My Site{% endblock %}</title>
    
    {# Bootstrap CSS #}
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    {# Custom CSS #}
    <link rel="stylesheet" href="{% static 'css/custom.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    {# Navbar #}
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">My Site</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link active" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/products/">Products</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/contact/">Contact</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    {# Alert Messages #}
    {% if messages %}
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        {% endfor %}
    {% endif %}

    <main class="container my-5">
        {% block content %}{% endblock %}
    </main>

    {# Footer #}
    <footer class="bg-dark text-white text-center py-3 mt-5">
        <p>&copy; 2024 My Site. All rights reserved.</p>
    </footer>

    {# Bootstrap JS #}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

#### Product List với Bootstrap Cards

```django
{# templates/products.html #}
{% extends 'base.html' %}

{% block title %}Products{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-md-6">
        <h1>Our Products</h1>
    </div>
    <div class="col-md-6 text-end">
        <form class="d-inline">
            <input type="text" class="form-control d-inline-block w-auto" placeholder="Search...">
            <button class="btn btn-primary">Search</button>
        </form>
    </div>
</div>

<div class="row">
    {% for product in products %}
        <div class="col-md-4 mb-4">
            <div class="card h-100 shadow-sm">
                {% if product.image %}
                    <img src="{{ product.image.url }}" class="card-img-top" alt="{{ product.name }}">
                {% else %}
                    <img src="{% static 'images/placeholder.jpg' %}" class="card-img-top" alt="No image">
                {% endif %}
                <div class="card-body">
                    <h5 class="card-title">{{ product.name }}</h5>
                    <p class="card-text">{{ product.description|truncatewords:15 }}</p>
                    <p class="text-primary fw-bold">${{ product.price }}</p>
                </div>
                <div class="card-footer">
                    <a href="{% url 'product_detail' product.id %}" class="btn btn-primary w-100">View Details</a>
                </div>
            </div>
        </div>
    {% empty %}
        <div class="col-12">
            <div class="alert alert-info">No products found.</div>
        </div>
    {% endfor %}
</div>

{# Pagination #}
{% if is_paginated %}
    <nav aria-label="Page navigation">
        <ul class="pagination justify-content-center">
            {% if page_obj.has_previous %}
                <li class="page-item">
                    <a class="page-link" href="?page={{ page_obj.previous_page_number }}">Previous</a>
                </li>
            {% endif %}
            
            <li class="page-item active">
                <span class="page-link">{{ page_obj.number }} of {{ page_obj.paginator.num_pages }}</span>
            </li>
            
            {% if page_obj.has_next %}
                <li class="page-item">
                    <a class="page-link" href="?page={{ page_obj.next_page_number }}">Next</a>
                </li>
            {% endif %}
        </ul>
    </nav>
{% endif %}
{% endblock %}
```

### 2. Tailwind CSS

#### Setup via CDN

```django
{# templates/base.html #}
{% load static %}
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}My Site{% endblock %}</title>
    
    {# Tailwind CSS #}
    <script src="https://cdn.tailwindcss.com"></script>
    
    {# Custom CSS #}
    <link rel="stylesheet" href="{% static 'css/custom.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body class="bg-gray-50">
    {# Navbar #}
    <nav class="bg-white shadow-lg">
        <div class="max-w-7xl mx-auto px-4">
            <div class="flex justify-between items-center py-4">
                <a href="/" class="text-2xl font-bold text-blue-600">My Site</a>
                <div class="space-x-4">
                    <a href="/" class="text-gray-700 hover:text-blue-600">Home</a>
                    <a href="/products/" class="text-gray-700 hover:text-blue-600">Products</a>
                    <a href="/contact/" class="text-gray-700 hover:text-blue-600">Contact</a>
                </div>
            </div>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 py-8">
        {% block content %}{% endblock %}
    </main>

    {# Footer #}
    <footer class="bg-gray-800 text-white text-center py-4 mt-12">
        <p>&copy; 2024 My Site. All rights reserved.</p>
    </footer>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

#### Product Grid với Tailwind

```django
{# templates/products.html #}
{% extends 'base.html' %}
{% load static %}

{% block title %}Products{% endblock %}

{% block content %}
<div class="mb-8">
    <h1 class="text-3xl font-bold mb-4">Our Products</h1>
    <div class="flex items-center space-x-4">
        <input type="text" placeholder="Search products..." 
               class="px-4 py-2 border rounded-lg flex-1">
        <button class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
            Search
        </button>
    </div>
</div>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {% for product in products %}
        <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow">
            {% if product.image %}
                <img src="{{ product.image.url }}" 
                     alt="{{ product.name }}"
                     class="w-full h-48 object-cover">
            {% else %}
                <img src="{% static 'images/placeholder.jpg' %}" 
                     alt="No image"
                     class="w-full h-48 object-cover bg-gray-200">
            {% endif %}
            
            <div class="p-4">
                <h3 class="text-xl font-bold mb-2">{{ product.name }}</h3>
                <p class="text-gray-600 mb-4">{{ product.description|truncatewords:15 }}</p>
                <div class="flex justify-between items-center">
                    <span class="text-2xl font-bold text-blue-600">${{ product.price }}</span>
                    <a href="{% url 'product_detail' product.id %}" 
                       class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                        View Details
                    </a>
                </div>
            </div>
        </div>
    {% empty %}
        <div class="col-span-3">
            <div class="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
                No products found.
            </div>
        </div>
    {% endfor %}
</div>
{% endblock %}
```

## 🚀 JavaScript Integration

### AJAX với Fetch API

```django
{# templates/base.html - add before closing body #}
<script src="{% static 'js/main.js' %}"></script>
{% block extra_js %}{% endblock %}
```

```javascript
// static/js/main.js
// Add to cart via AJAX
function addToCart(productId, quantity = 1) {
    fetch('/api/cart/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Added to cart!', 'success');
            updateCartBadge();
        } else {
            showNotification(data.error || 'Something went wrong', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Failed to add to cart', 'error');
    });
}

// Update cart badge
function updateCartBadge() {
    fetch('/api/cart/count/')
        .then(response => response.json())
        .then(data => {
            const badge = document.getElementById('cart-badge');
            if (badge) {
                badge.textContent = data.count;
                badge.classList.remove('hidden');
                if (data.count === 0) {
                    badge.classList.add('hidden');
                }
            }
        });
}

// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    notification.style.zIndex = '9999';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Attach event listeners
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            const quantity = this.dataset.quantity || 1;
            addToCart(productId, quantity);
        });
    });
    
    // Initialize tooltips (Bootstrap)
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Update cart badge on load
    updateCartBadge();
});
```

### Search với AJAX

```javascript
// static/js/search.js
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('search-results');
    
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            
            clearTimeout(searchTimeout);
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    searchProducts(query);
                }, 300);
            } else {
                resultsContainer.innerHTML = '';
            }
        });
    }
});

function searchProducts(query) {
    fetch(`/api/search/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displayResults(data.results);
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}

function displayResults(results) {
    const container = document.getElementById('search-results');
    
    if (results.length === 0) {
        container.innerHTML = '<p class="text-muted">No results found</p>';
        return;
    }
    
    let html = '<div class="list-group">';
    results.forEach(item => {
        html += `
            <a href="${item.url}" class="list-group-item list-group-item-action">
                <h6>${item.title}</h6>
                <p class="mb-1 small text-muted">${item.description}</p>
            </a>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
}
```

## 🎯 Complete Example: E-commerce

```django
{# templates/product_list.html #}
{% extends 'base.html' %}
{% load static %}

{% block title %}Products - TechStore{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-md-8">
        <h1 class="h2 mb-0">Products</h1>
    </div>
    <div class="col-md-4">
        <input type="text" id="search-input" class="form-control" placeholder="Search products...">
        <div id="search-results" class="mt-2"></div>
    </div>
</div>

<div class="row" id="product-grid">
    {% for product in products %}
        <div class="col-md-4 mb-4">
            <div class="card product-card h-100">
                {% if product.image %}
                    <img src="{{ product.image.url }}" class="card-img-top" alt="{{ product.name }}">
                {% endif %}
                
                <div class="card-body">
                    <h5 class="card-title">{{ product.name }}</h5>
                    <p class="card-text">{{ product.description|truncatewords:15 }}</p>
                    
                    {% if product.in_stock %}
                        <span class="badge bg-success">In Stock</span>
                    {% else %}
                        <span class="badge bg-danger">Out of Stock</span>
                    {% endif %}
                    
                    <p class="h4 text-primary mt-3">${{ product.price }}</p>
                </div>
                
                <div class="card-footer">
                    <a href="{% url 'product_detail' product.id %}" class="btn btn-primary w-100 mb-2">
                        View Details
                    </a>
                    <button class="btn btn-success w-100 add-to-cart" 
                            data-product-id="{{ product.id }}"
                            {% if not product.in_stock %}disabled{% endif %}>
                        <i class="bi bi-cart-plus"></i> Add to Cart
                    </button>
                </div>
            </div>
        </div>
    {% endfor %}
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/cart.js' %}"></script>
<script src="{% static 'js/search.js' %}"></script>
{% endblock %}
```

## ✅ Checklist

- [ ] Tích hợp Bootstrap hoặc Tailwind CSS
- [ ] Tạo responsive layout
- [ ] Thêm AJAX functionality
- [ ] Tạo interactive UI với JavaScript
- [ ] Handle form submission với AJAX
- [ ] Show notifications và messages
- [ ] Implement search functionality
- [ ] Add loading states
