"""
Context Processors for store app
Provides global data to all templates
"""


def site_settings(request):
    """Provide global site settings to all templates"""
    return {
        'site_name': 'TechStore 2025',
        'site_tagline': 'Premium E-commerce Platform',
        'current_year': 2024,
        'company_email': 'support@techstore.com',
        'company_phone': '1-800-TECHSTORE',
        'company_address': '123 Tech Avenue, San Francisco, CA 94103',
    }


def cart_info(request):
    """Provide cart information for authenticated users"""
    cart_info = {
        'cart_count': 0,
        'cart_total': 0,
        'cart_items': [],
    }
    
    if request.user.is_authenticated:
        # Get customer if exists
        try:
            customer = request.user.customer_profile
            cart_items = customer.cart_items.select_related('product').all()
            cart_info['cart_items'] = cart_items
            cart_info['cart_count'] = cart_items.count()
            cart_info['cart_total'] = sum(
                item.product.price * item.quantity 
                for item in cart_items
            )
        except AttributeError:
            pass
    
    return cart_info


def navigation_categories(request):
    """Provide categories for navigation menu"""
    from .models import Category
    
    return {
        'nav_categories': Category.objects.filter(
            is_active=True, 
            parent__isnull=True
        )[:8],
    }


def featured_products(request):
    """Provide featured products for sidebar"""
    from .models import Product
    
    return {
        'sidebar_featured': Product.objects.filter(
            is_featured=True,
            status='published'
        )[:5],
    }

