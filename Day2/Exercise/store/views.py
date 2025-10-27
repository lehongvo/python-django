from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import UserCreationForm
from .models import Product, Category, Tag, Order, OrderItem, Customer
from django.db.models import Q


def home(request):
    """Homepage with featured products"""
    featured_products = Product.objects.filter(is_featured=True, status='published')[:6]
    categories = Category.objects.filter(is_active=True)
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)


def product_list(request):
    """List all products with filters"""
    products = Product.objects.filter(status='published')
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
        category = get_object_or_404(Category, slug=category_slug)
    else:
        category = None
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Filter by featured
    featured_only = request.GET.get('featured') == 'true'
    if featured_only:
        products = products.filter(is_featured=True)
    
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': category,
        'search_query': search_query,
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    """Product detail page"""
    product = get_object_or_404(Product, slug=slug, status='published')
    related_products = Product.objects.filter(
        category=product.category,
        status='published'
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)


def category_list(request):
    """List all categories"""
    categories = Category.objects.filter(is_active=True)
    context = {
        'categories': categories,
    }
    return render(request, 'store/category_list.html', context)


def checkout(request):
    """Checkout page and order creation"""
    # Handle POST - Create order
    if request.method == 'POST':
        # Get cart data from request (passed from JavaScript)
        cart_data = request.POST.get('cart_data', '[]')
        import json
        cart_items = json.loads(cart_data)
        
        if not cart_items:
            messages.error(request, 'Your cart is empty!')
            return redirect('store:cart')
        
        # Get or create customer
        if request.user.is_authenticated:
            customer, created = Customer.objects.get_or_create(
                email=request.user.email,
                defaults={
                    'name': request.user.get_full_name() or request.user.username,
                    'phone': request.POST.get('phone', ''),
                    'address': request.POST.get('address', ''),
                    'city': request.POST.get('city', ''),
                    'state': request.POST.get('state', ''),
                    'postal_code': request.POST.get('postal_code', ''),
                    'country': request.POST.get('country', 'USA'),
                }
            )
            
            # If customer exists, update info
            if not created:
                customer.name = request.user.get_full_name() or request.user.username
                customer.phone = request.POST.get('phone', '')
                customer.address = request.POST.get('address', '')
                customer.city = request.POST.get('city', '')
                customer.state = request.POST.get('state', '')
                customer.postal_code = request.POST.get('postal_code', '')
                customer.country = request.POST.get('country', 'USA')
                customer.save()
        else:
            # For non-authenticated users, create temp customer
            customer = Customer.objects.create(
                name=request.POST.get('name', 'Guest'),
                email=request.POST.get('email', 'guest@example.com'),
                phone=request.POST.get('phone', ''),
                address=request.POST.get('address', ''),
                city=request.POST.get('city', ''),
                state=request.POST.get('state', ''),
                postal_code=request.POST.get('postal_code', ''),
                country=request.POST.get('country', 'USA'),
            )
        
        # Calculate totals
        subtotal = sum(float(item['price']) * int(item['quantity']) for item in cart_items)
        tax = subtotal * 0.1
        grand_total = subtotal + tax
        
        # Generate order number
        from datetime import datetime
        import random
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        
        # Create order
        order = Order.objects.create(
            order_number=order_number,
            customer=customer,
            status='processing',
            total_amount=grand_total,
            shipping_address=request.POST.get('address', customer.address),
            shipping_city=request.POST.get('city', customer.city),
            shipping_state=request.POST.get('state', customer.state),
            shipping_postal_code=request.POST.get('postal_code', customer.postal_code),
            shipping_country=request.POST.get('country', customer.country),
        )
        
        # Create order items
        for item in cart_items:
            try:
                product = Product.objects.get(id=item['product_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=int(item['quantity']),
                    price=float(item['price']),
                )
            except Product.DoesNotExist:
                pass
        
        messages.success(request, f'Order {order_number} placed successfully!')
        
        # Clear cart
        return redirect('store:order_tracking') + f'?order_number={order_number}'
    
    # GET - Show checkout page
    # Get product from query params (for Buy Now)
    product_id = request.GET.get('product')
    quantity = request.GET.get('quantity', 1)
    
    cart_products = []
    subtotal = 0
    tax = 0
    grand_total = 0
    
    if product_id:
        # Single product checkout (Buy Now)
        try:
            product = Product.objects.get(id=product_id, status='published')
            subtotal = float(product.price) * int(quantity)
            tax = subtotal * 0.1  # 10% tax
            grand_total = subtotal + tax
            
            cart_products = [{
                'product': product,
                'quantity': int(quantity),
                'subtotal': subtotal
            }]
        except Product.DoesNotExist:
            messages.error(request, 'Product not found')
            return redirect('store:product_list')
    else:
        # Get cart from localStorage (for now, show message to add products)
        messages.info(request, 'Your cart is empty. Add some products first!')
    
    context = {
        'cart_products': cart_products,
        'subtotal': subtotal,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/checkout.html', context)


def user_login(request):
    """User login page"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            
            # Redirect to next page if specified
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('store:account')
        else:
            messages.error(request, 'Invalid username or password.')
    
    context = {}
    return render(request, 'store/login.html', context)


def register(request):
    """User registration page"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create customer record
            customer = Customer.objects.create(
                name=user.username,
                email=user.email if user.email else f"{user.username}@example.com",
            )
            
            # Auto login after registration
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome! Your account has been created, {username}!')
                return redirect('store:account')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'store/register.html', context)


def account(request):
    """User account page"""
    # Check if user is authenticated
    if request.user.is_authenticated:
        user = request.user
        
        # Get customer info if exists
        customer = None
        try:
            customer = Customer.objects.get(email=user.email)
        except Customer.DoesNotExist:
            pass
        
        # Get user orders
        orders = []
        if customer:
            orders = Order.objects.filter(customer=customer).order_by('-order_date')[:10]
    else:
        # For non-authenticated users, show login prompt
        orders = []
        customer = None
        user = None
    
    context = {
        'user': user,
        'customer': customer,
        'orders': orders,
    }
    return render(request, 'store/account.html', context)


def account_settings(request):
    """User account settings page"""
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to access settings.')
        return redirect('store:user_login')
    
    user = request.user
    
    # Get or create customer
    customer, created = Customer.objects.get_or_create(
        email=user.email,
        defaults={
            'name': user.get_full_name() or user.username,
            'phone': '',
            'address': '',
            'city': '',
            'state': '',
            'postal_code': '',
            'country': 'USA',
        }
    )
    
    if request.method == 'POST':
        # Update user info
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        # Update customer info
        customer.name = f"{user.first_name} {user.last_name}".strip() or user.username
        customer.email = user.email
        customer.phone = request.POST.get('phone', '')
        customer.address = request.POST.get('address', '')
        customer.city = request.POST.get('city', '')
        customer.state = request.POST.get('state', '')
        customer.postal_code = request.POST.get('postal_code', '')
        customer.country = request.POST.get('country', 'USA')
        customer.save()
        
        messages.success(request, 'Settings updated successfully!')
        return redirect('store:account_settings')
    
    context = {
        'user': user,
        'customer': customer,
    }
    return render(request, 'store/account_settings.html', context)


def cart(request):
    """Shopping cart page"""
    return render(request, 'store/cart.html')


def logout_view(request):
    """Logout user"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('store:home')


def order_tracking(request):
    """Order tracking page"""
    order_number = request.GET.get('order_number', '')
    
    order = None
    if order_number:
        try:
            order = Order.objects.select_related('customer').prefetch_related('items__product').get(
                order_number=order_number
            )
        except Order.DoesNotExist:
            messages.error(request, f'Order {order_number} not found')
    
    context = {
        'order': order,
        'order_number': order_number,
    }
    return render(request, 'store/order_tracking.html', context)
