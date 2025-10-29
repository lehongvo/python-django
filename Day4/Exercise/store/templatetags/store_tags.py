"""
Custom template tags for store app
"""

from django import template
from datetime import datetime

register = template.Library()


@register.simple_tag
def current_time(format_string):
    """Display current time in specified format"""
    return datetime.now().strftime(format_string)


@register.simple_tag
def current_year():
    """Display current year"""
    return datetime.now().year


@register.simple_tag
def calculate_total(price, quantity, discount=0):
    """Calculate total with discount"""
    try:
        total = float(price) * int(quantity)
        if discount:
            total *= (1 - float(discount) / 100)
        return f"${total:.2f}"
    except (ValueError, TypeError):
        return "$0.00"


@register.simple_tag(takes_context=True)
def absolute_url(context, url_name, **kwargs):
    """Generate absolute URL with current request"""
    request = context.get('request')
    if not request:
        return url_name
    
    from django.urls import reverse
    try:
        return request.build_absolute_uri(reverse(url_name, kwargs=kwargs))
    except:
        return url_name


@register.inclusion_tag('store/components/product_card.html')
def show_product_card(product, show_description=True, class_name=''):
    """Render product card component"""
    return {
        'product': product,
        'show_description': show_description,
        'class_name': class_name,
    }


@register.inclusion_tag('store/components/pagination.html')
def show_pagination(page_obj, page_param='page'):
    """Render pagination component"""
    return {
        'page_obj': page_obj,
        'page_param': page_param,
    }


@register.inclusion_tag('store/components/user_badge.html')
def show_user_badge(user):
    """Render user badge component"""
    return {
        'user': user,
        'is_staff': user.is_staff if user.is_authenticated else False,
        'is_superuser': user.is_superuser if user.is_authenticated else False,
    }

