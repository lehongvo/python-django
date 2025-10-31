from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from .models import Product, Category, Tag, Order, OrderItem, Customer, Subscriber, PromoCode
from django.db.models import Q, F, Case, When, Value, FloatField, ExpressionWrapper
from django.http import JsonResponse
from django.urls import reverse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.mail import send_mail
import random
from datetime import timedelta
from .models import EmailOTP
from .utils import assign_welcome_promo_and_email, claim_unused_promos
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import os
import secrets

def _get_eth_account():
    try:
        from eth_account.messages import encode_defunct
        from eth_account import Account
        return Account, encode_defunct
    except Exception:
        return None, None


def web3_challenge(request):
    """Issue a one-time nonce for MetaMask signature."""
    # Simple rate limit: 20/min per IP
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    key = f"rl:auth:challenge:{ip}"
    count = cache.get(key, 0)
    if count >= 20:
        return JsonResponse({'error': 'Too many requests'}, status=429)
    cache.set(key, count + 1, 60)

    nonce = secrets.token_hex(16)
    request.session['web3_nonce'] = nonce
    return JsonResponse({'nonce': nonce})


@csrf_exempt
def web3_verify(request):
    """Verify signature for the issued nonce and store verified address in session.
    If eth_account isn't available, allow in DEBUG for development.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    # Simple rate limit: 20/min per IP
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    key = f"rl:auth:verify:{ip}"
    count = cache.get(key, 0)
    if count >= 20:
        return JsonResponse({'error': 'Too many requests'}, status=429)
    cache.set(key, count + 1, 60)
    import json as _json
    try:
        data = _json.loads(request.body or '{}')
    except Exception:
        data = {}
    address = (data.get('address') or '').lower()
    signature = data.get('signature')
    nonce = request.session.get('web3_nonce')
    if not (address and signature and nonce):
        return JsonResponse({'error': 'Missing fields'}, status=400)

    Account, encode_defunct = _get_eth_account()
    verified = False
    if Account and encode_defunct:
        try:
            msg = encode_defunct(text=f"TechStore login: {nonce}")
            recovered = Account.recover_message(msg, signature=signature)
            verified = recovered.lower() == address
        except Exception:
            verified = False
    else:
        # Dev fallback
        verified = settings.DEBUG

    if not verified:
        return JsonResponse({'error': 'Signature verification failed'}, status=400)

    request.session['web3_address_verified'] = address
    # One-time use
    request.session['web3_nonce'] = None
    return JsonResponse({'ok': True, 'next': reverse('store:web3_complete')})


def web3_complete(request):
    """After successful signature, let user set username/password and create account."""
    address = request.session.get('web3_address_verified')
    if not address:
        messages.error(request, 'MetaMask verification required.')
        return redirect('store:user_login')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        email = request.POST.get('email', '').strip().lower() or f"{address[:6]}@web3.local"
        if not (username and password1 and password2):
            messages.error(request, 'All fields are required.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        else:
            from django.contrib.auth.models import User
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
            else:
                user = User.objects.create_user(username=username, password=password1, email=email)
                Customer.objects.update_or_create(
                    email=email,
                    defaults={
                        'user': user,
                        'name': user.get_full_name() or username,
                        'phone': '', 'address': '', 'city': '', 'state': '', 'postal_code': '', 'country': 'USA'
                    },
                )
                # login and set JWT cookies
                login(request, user)
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)
                response = redirect('store:account')
                secure_flag = not settings.DEBUG
                response.set_cookie('access_token', access_token, max_age=60*60, httponly=True, secure=secure_flag, samesite='Lax', path='/')
                response.set_cookie('refresh_token', refresh_token, max_age=7*24*60*60, httponly=True, secure=secure_flag, samesite='Lax', path='/')
                messages.success(request, 'Account created via MetaMask and logged in!')
                # clear session flags
                request.session['web3_address_verified'] = None
                return response

    return render(request, 'store/web3_complete.html', {'address': address})


def home(request):
    """Homepage with featured products"""
    # Order by dynamic discount percentage (computed from compare_price and price), then featured
    from django.core.paginator import Paginator
    computed_discount_expr = Case(
        When(
            compare_price__gt=F('price'),
            then=ExpressionWrapper(
                (F('compare_price') - F('price')) * 100.0 / F('compare_price'),
                output_field=FloatField(),
            ),
        ),
        default=Value(0.0),
        output_field=FloatField(),
    )
    featured_products = (
        Product.objects.filter(status='published')
        .annotate(computed_discount_percent=computed_discount_expr)
        .order_by('-computed_discount_percent', '-is_featured')[:6]
    )
    try:
        cat_limit = int(request.GET.get('cat_limit', 6))
    except ValueError:
        cat_limit = 6
    try:
        cat_page = int(request.GET.get('cat_page', 1))
    except ValueError:
        cat_page = 1
    categories_qs = Category.objects.filter(is_active=True).order_by('name')
    cat_paginator = Paginator(categories_qs, max(1, min(cat_limit, 18)))
    cat_page_obj = cat_paginator.get_page(cat_page)
    categories = cat_page_obj.object_list
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'cat_paginator': cat_paginator,
        'cat_page_obj': cat_page_obj,
        'cat_limit': cat_limit,
        'cat_limits': [6, 9, 12, 15],
    }
    return render(request, 'store/home.html', context)


def product_list(request):
    """List all products with filters"""
    products = Product.objects.filter(status='published')
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
        current_category_obj = get_object_or_404(Category, slug=category_slug)
    else:
        current_category_obj = None
    
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

    # Sort
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')

    # Pagination
    from django.core.paginator import Paginator
    try:
        limit = int(request.GET.get('limit', 24))
    except ValueError:
        limit = 24
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    paginator = Paginator(products, max(1, min(limit, 100)))
    page_obj = paginator.get_page(page)
    products = page_obj.object_list
    
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': category_slug,  # Pass slug instead of object
        'current_category_obj': current_category_obj,  # Keep object for other uses
        'search_query': search_query,
        'sort_by': sort_by,
        'paginator': paginator,
        'page_obj': page_obj,
        'limit': limit,
        'limits': [12, 24, 36, 48, 60],
        'page': page,
        'total_count': paginator.count,
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
    """List all categories with pagination"""
    from django.core.paginator import Paginator
    
    # Get all active categories
    categories_qs = Category.objects.filter(is_active=True).order_by('name')
    
    # Pagination
    try:
        limit = int(request.GET.get('limit', 12))
    except ValueError:
        limit = 12
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    
    paginator = Paginator(categories_qs, max(1, min(limit, 24)))
    page_obj = paginator.get_page(page)
    categories = page_obj.object_list
    
    context = {
        'categories': categories,
        'paginator': paginator,
        'page_obj': page_obj,
        'limit': limit,
        'limits': [6, 9, 12, 15, 18, 21, 24],
        'page': page,
        'total_count': paginator.count,
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
        # Shipping method/fee
        shipping_method = request.POST.get('shipping_method', 'standard')
        shipping_fee = 0.0 if shipping_method == 'standard' else 9.99
        tax = subtotal * 0.1
        # Promo code (optional)
        promo_code = (request.POST.get('promo_code') or '').strip().upper()
        discount_amount = 0.0
        promo_obj = None
        if promo_code:
            qs = PromoCode.objects.filter(promo_code=promo_code, is_used=False)
            if request.user.is_authenticated:
                qs = qs.filter(Q(user__isnull=True) | Q(user=request.user))
            else:
                qs = qs.filter(user__isnull=True)
            promo_obj = qs.first()
            if promo_obj:
                discount_amount = (subtotal + tax + shipping_fee) * (promo_obj.promo_amount / 100.0)
        grand_total = subtotal + tax + shipping_fee - discount_amount
        
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
        
        # Send order confirmation email
        try:
            est_days = 5 if shipping_method == 'standard' else 2
            from datetime import timedelta
            delivery_eta = (timezone.now() + timedelta(days=est_days)).date()
            email_ctx = {
                'order_number': order_number,
                'customer': customer,
                'items': cart_items,
                'subtotal': subtotal,
                'tax': tax,
                'shipping_fee': shipping_fee,
                'total': grand_total,
                'promo_code': promo_obj.promo_code if promo_obj else None,
                'promo_amount': promo_obj.promo_amount if promo_obj else None,
                'discount_amount': discount_amount if promo_obj else 0.0,
                'shipping_method': 'Express' if shipping_method != 'standard' else 'Standard',
                'delivery_eta': delivery_eta,
                'order': order,
                'track_url': request.build_absolute_uri(reverse('store:order_tracking') + f'?order_number={order_number}')
            }
            # Build absolute URLs for images
            for it in email_ctx['items']:
                img = None
                try:
                    p = Product.objects.get(id=it['product_id'])
                    # enrich for email rendering
                    it['name'] = getattr(p, 'name', it.get('name'))
                    if getattr(p, 'image', None) and p.image:
                        img = request.build_absolute_uri(p.image.url)
                except Exception:
                    pass
                it['image_url'] = img or f"https://picsum.photos/seed/{it.get('product_id','img')}/200/150"

            subject = f'Your order {order_number} is confirmed — TechStore 2025'
            html_body = render_to_string('emails/order_confirmation.html', email_ctx)
            text_body = render_to_string('emails/order_confirmation.txt', email_ctx)
            msg = EmailMultiAlternatives(subject, text_body, to=[customer.email])
            msg.attach_alternative(html_body, 'text/html')
            msg.send(fail_silently=True)
        except Exception:
            pass

        # Mark promo used after successful order
        if promo_obj:
            try:
                promo_obj.is_used = True
                if request.user.is_authenticated and promo_obj.user_id is None:
                    promo_obj.user = request.user
                promo_obj.save(update_fields=['is_used', 'user'])
            except Exception:
                pass

        messages.success(request, f'Order {order_number} placed successfully! A confirmation email has been sent.')
        
        # Clear server-side cart for authenticated users
        try:
            if request.user.is_authenticated:
                from .models import Cart
                Cart.objects.filter(customer=customer).delete()
        except Exception:
            pass

        # Redirect to tracking page with query param
        tracking_url = reverse('store:order_tracking') + f'?order_number={order_number}&cleared=1'
        return redirect(tracking_url)
    
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
            
            # Issue JWT tokens and set cookies
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            next_url = request.GET.get('next') or 'store:account'
            response = redirect(next_url)

            secure_flag = not settings.DEBUG
            # access cookie ~1 hour
            response.set_cookie(
                'access_token',
                access_token,
                max_age=60 * 60,
                httponly=True,
                secure=secure_flag,
                samesite='Lax',
                path='/',
            )
            # refresh cookie ~7 days
            response.set_cookie(
                'refresh_token',
                refresh_token,
                max_age=7 * 24 * 60 * 60,
                httponly=True,
                secure=secure_flag,
                samesite='Lax',
                path='/',
            )
            # Ensure user has at least 8 promo codes on first login/new email
            try:
                existing = 0
                try:
                    existing = user.promo_codes.count()
                except Exception:
                    existing = 0
                if existing <= 0:
                    # First time → mint 8 and send welcome email with codes
                    assign_welcome_promo_and_email(user, count=8)
                elif existing < 8:
                    # Top up silently to 8 (no email spam). Cron will raise to 10 later.
                    claim_unused_promos(user, 8 - existing)
            except Exception:
                pass
            return response
        else:
            messages.error(request, 'Invalid username or password.')
    
    context = {}
    return render(request, 'store/login.html', context)


def register(request):
    """Two-step registration requiring email OTP verification."""
    if request.method == 'POST':
        step = request.POST.get('step', 'request_otp')
        email = request.POST.get('email', '').strip().lower()
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if step == 'request_otp':
            if not email:
                messages.error(request, 'Email is required.')
                return render(request, 'store/register.html', {'step': 'request_otp'})
            # Ensure email not already used by a user/customer
            from django.contrib.auth.models import User
            if User.objects.filter(email=email).exists() or Customer.objects.filter(email=email).exists():
                messages.error(request, 'Email is already in use.')
                return render(request, 'store/register.html', {'step': 'request_otp'})
            # Create OTP
            code = f"{random.randint(100000, 999999)}"
            expires_at = timezone.now() + timedelta(minutes=10)
            EmailOTP.objects.create(email=email, code=code, expires_at=expires_at)
            # Send OTP via email
            try:
                from django.conf import settings as dj_settings
                send_mail(
                    subject='Your verification code',
                    message=f'Your OTP code is: {code}. It expires in 10 minutes.',
                    from_email=dj_settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
            except Exception as e:
                messages.error(request, f"Failed to send OTP email: {e}")
            messages.success(request, 'OTP sent to your email. Please check your inbox.')
            context = {'prefill_email': email, 'step': 'verify_otp'}
            try:
                from django.conf import settings as dj_settings
                if dj_settings.DEBUG and str(dj_settings.EMAIL_BACKEND).endswith('console.EmailBackend'):
                    context['dev_otp'] = code
            except Exception:
                pass
            return render(request, 'store/register.html', context)

        elif step == 'verify_otp':
            otp = request.POST.get('otp', '').strip()
            if not (email and otp and username and password1 and password2):
                messages.error(request, 'All fields are required.')
                return render(request, 'store/register.html', {
                    'prefill_email': email,
                    'step': 'verify_otp',
                    'prefill_username': username,
                })
            if password1 != password2:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'store/register.html', {
                    'prefill_email': email,
                    'step': 'verify_otp',
                    'prefill_username': username,
                })
            if not (otp.isdigit() and len(otp) == 6):
                messages.error(request, 'OTP must be 6 digits.')
                return render(request, 'store/register.html', {
                    'prefill_email': email,
                    'step': 'verify_otp',
                    'prefill_username': username,
                })

            # Validate OTP
            now = timezone.now()
            otp_qs = EmailOTP.objects.filter(email=email, is_used=False, expires_at__gt=now)
            record = otp_qs.filter(code=otp).order_by('-created_at').first()
            if not record:
                messages.error(request, 'OTP not found. Please request a new code.')
                return render(request, 'store/register.html', {
                    'prefill_email': email,
                    'step': 'verify_otp',
                    'prefill_username': username,
                })

            from django.contrib.auth.models import User
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
                return render(request, 'store/register.html', {
                    'prefill_email': email,
                    'step': 'verify_otp',
                    'prefill_username': username,
                })
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email is already in use.')
                return render(request, 'store/register.html', {
                    'prefill_email': email,
                    'step': 'verify_otp',
                    'prefill_username': username,
                })

            created_user = User.objects.create_user(username=username, email=email, password=password1)
            Customer.objects.update_or_create(
                email=email,
                defaults={
                    'user': created_user,
                    'name': created_user.get_full_name() or username,
                    'phone': '', 'address': '', 'city': '', 'state': '', 'postal_code': '', 'country': 'USA'
                },
            )
            record.is_used = True
            record.save(update_fields=['is_used'])
            try:
                assign_welcome_promo_and_email(created_user, count=8)
            except Exception:
                pass
            messages.success(request, 'Your account has been created successfully. Please log in to continue.')
            return redirect('store:user_login')

        # Fallback re-render
        return render(request, 'store/register.html', {'step': 'request_otp', 'prefill_email': email})

    # GET: show initial step to request OTP
    return render(request, 'store/register.html', {'step': 'request_otp'})


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
            orders = Order.objects.filter(customer=customer).order_by('-order_date')[:4]
            pending_count = Order.objects.filter(customer=customer, status='processing').count()
        else:
            pending_count = 0
    else:
        # For non-authenticated users, show login prompt
        orders = []
        customer = None
        user = None
        pending_count = 0
    
    context = {
        'user': user,
        'customer': customer,
        'orders': orders,
        'pending_count': pending_count,
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


def account_addresses(request):
    """User addresses page"""
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to view addresses.')
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
        # Update customer address
        customer.phone = request.POST.get('phone', '')
        customer.address = request.POST.get('address', '')
        customer.city = request.POST.get('city', '')
        customer.state = request.POST.get('state', '')
        customer.postal_code = request.POST.get('postal_code', '')
        customer.country = request.POST.get('country', 'USA')
        customer.save()
        
        messages.success(request, 'Address updated successfully!')
        return redirect('store:account_addresses')
    
    context = {
        'user': user,
        'customer': customer,
    }
    return render(request, 'store/account_addresses.html', context)


def account_orders(request):
    """User orders page"""
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to view your orders.')
        return redirect('store:user_login')
    
    user = request.user
    
    # Get customer info
    customer = None
    try:
        customer = Customer.objects.get(email=user.email)
    except Customer.DoesNotExist:
        pass
    
    # Get user orders
    orders = []
    if customer:
        orders = Order.objects.filter(customer=customer).order_by('-order_date').select_related('customer').prefetch_related('items__product')
    
    context = {
        'user': user,
        'customer': customer,
        'orders': orders,
    }
    return render(request, 'store/account_orders.html', context)


def account_vouchers(request):
    """User vouchers page"""
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to view your vouchers.')
        return redirect('store:user_login')

    user = request.user
    vouchers = PromoCode.objects.filter(user=user).order_by('-created_at')
    used_count = vouchers.filter(is_used=True).count()
    unused_count = vouchers.filter(is_used=False).count()

    context = {
        'user': user,
        'vouchers': vouchers,
        'used_count': used_count,
        'unused_count': unused_count,
    }
    return render(request, 'store/account_vouchers.html', context)

def cart(request):
    """Shopping cart page"""
    return render(request, 'store/cart.html')


def logout_view(request):
    """Logout user"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    response = redirect('store:home')
    # Clear JWT cookies
    response.delete_cookie('access_token', path='/')
    response.delete_cookie('refresh_token', path='/')
    return response


def order_tracking(request):
    """Order tracking page"""
    order_number = request.GET.get('order_number', '')
    
    # If no order number provided, default to the user's most recent order
    if not order_number and request.user.is_authenticated:
        try:
            customer = Customer.objects.get(email=request.user.email)
            latest = (
                Order.objects
                .filter(customer=customer)
                .order_by('-order_date')
                .first()
            )
            if latest:
                order_number = latest.order_number
        except Customer.DoesNotExist:
            pass
    
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


from django.http import JsonResponse

def my_unused_promos_api(request):
    """Return the current user's unused promo codes as JSON.
    Used by checkout promo picker. Returns empty list if not authenticated.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'promos': []})
    codes = (
        PromoCode.objects
        .filter(user=request.user, is_used=False)
        .order_by('-created_at')
        .values('promo_code', 'promo_amount')
    )
    return JsonResponse({'promos': list(codes)})


# Support pages
def help_center(request):
    return render(request, 'store/support_help_center.html')


def contact_us(request):
    return render(request, 'store/support_contact.html')


def shipping_info(request):
    return render(request, 'store/support_shipping.html')


def returns_policy(request):
    return render(request, 'store/support_returns.html')


def subscribe(request):
    """Subscribe to newsletter via AJAX."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    # Rate limit: 20/min per IP
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    key = f"rl:subscribe:{ip}"
    count = cache.get(key, 0)
    if count >= 20:
        return JsonResponse({'error': 'Too many requests'}, status=429)
    cache.set(key, count + 1, 60)

    email = request.POST.get('email') or (request.headers.get('Content-Type','').startswith('application/json') and __import__('json').loads(request.body or '{}').get('email'))
    if not email:
        return JsonResponse({'error': 'Email is required'}, status=400)
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({'error': 'Invalid email'}, status=400)

    sub, created = Subscriber.objects.get_or_create(email=email)
    # Send welcome email (HTML + text)
    try:
        context = {
            'email': email,
            'site_name': 'TechStore 2025',
        }
        subject = 'Welcome to TechStore — Exclusive Deals Are Coming Your Way!'
        text_body = render_to_string('emails/subscribed.txt', context)
        html_body = render_to_string('emails/subscribed.html', context)
        msg = EmailMultiAlternatives(subject, text_body, to=[email])
        msg.attach_alternative(html_body, 'text/html')
        msg.send(fail_silently=True)
    except Exception:
        pass

    return JsonResponse({'message': 'Subscribed successfully' if created else 'You are already subscribed'})


@login_required
def delete_account_request(request):
    """Step 1: send OTP to user's email for account deletion confirmation."""
    user = request.user
    email = user.email
    if not email:
        messages.error(request, 'Your account has no email address. Please add an email first in Settings.')
        return redirect('store:account_settings')

    # Create OTP valid for 10 minutes
    code = f"{random.randint(100000, 999999)}"
    expires_at = timezone.now() + timedelta(minutes=10)
    EmailOTP.objects.create(email=email, code=code, expires_at=expires_at)

    # Send email
    try:
        from django.conf import settings as dj_settings
        context = { 'code': code, 'user': user }
        subject = 'Confirm Account Deletion — Your OTP Code'
        text_body = f"Your OTP code is {code}. It expires in 10 minutes. Enter this code to confirm deleting your account."
        send_mail(subject, text_body, dj_settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
    except Exception as e:
        messages.error(request, f"Failed to send OTP email: {e}")
        return redirect('store:account_settings')

    return render(request, 'store/account_delete.html', { 'email': email })


@login_required
def delete_account_confirm(request):
    """Step 2: verify OTP and delete the account permanently."""
    if request.method != 'POST':
        return redirect('store:account_settings')

    otp = request.POST.get('otp', '').strip()
    if not (otp.isdigit() and len(otp) == 6):
        messages.error(request, 'OTP must be 6 digits.')
        return render(request, 'store/account_delete.html', { 'email': request.user.email })

    now = timezone.now()
    rec = EmailOTP.objects.filter(email=request.user.email, is_used=False, expires_at__gt=now, code=otp).order_by('-created_at').first()
    if not rec:
        messages.error(request, 'Invalid or expired OTP. Please request a new code.')
        return render(request, 'store/account_delete.html', { 'email': request.user.email })

    # Mark used and delete account data
    rec.is_used = True
    rec.save(update_fields=['is_used'])

    from django.contrib.auth.models import User
    user = request.user
    logout(request)
    try:
        # Detach related customer if any, then delete user (on_delete CASCADE may handle)
        Customer.objects.filter(user=user).update(user=None)
        User.objects.filter(id=user.id).delete()
    finally:
        messages.success(request, 'Your account has been deleted. We’re sorry to see you go!')
        response = redirect('store:home')
        response.delete_cookie('access_token', path='/')
        response.delete_cookie('refresh_token', path='/')
    return response
