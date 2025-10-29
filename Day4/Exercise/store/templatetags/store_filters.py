"""
Custom template filters for store app
"""

from django import template
from datetime import datetime

register = template.Library()


@register.filter
def format_vnd(amount):
    """Format amount as US Dollar (keeping old name for compatibility)"""
    try:
        return f"${float(amount):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"


@register.filter
def format_usd(amount):
    """Format amount as US Dollar"""
    try:
        return f"${float(amount):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"


@register.filter
def in_stock(product):
    """Check if product is in stock"""
    return product.stock > 0


@register.filter
def discount_percent(original, current):
    """Calculate discount percentage"""
    try:
        if float(original) <= 0:
            return 0
        return int((float(original) - float(current)) / float(original) * 100)
    except (ValueError, TypeError):
        return 0


@register.filter
def multiply(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def price_with_tax(price, tax_rate=0.1):
    """Calculate price with tax"""
    try:
        return float(price) * (1 + float(tax_rate))
    except (ValueError, TypeError):
        return 0


@register.filter
def truncate_smart(text, length):
    """Smart truncate that doesn't cut words"""
    try:
        if len(text) <= int(length):
            return text
        return text[:int(length)].rsplit(' ', 1)[0] + '...'
    except (ValueError, TypeError):
        return text


@register.filter
def reading_time(content):
    """Calculate reading time in minutes"""
    try:
        words = len(str(content).split())
        minutes = words // 200  # Average reading speed: 200 words/min
        return max(1, minutes)
    except (ValueError, TypeError):
        return 1


@register.filter
def format_phone(phone):
    """Format phone number"""
    try:
        phone = str(phone).replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        if len(phone) == 10:
            return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"
        elif len(phone) == 11:
            return f"{phone[:1]}-{phone[1:4]}-{phone[4:7]}-{phone[7:]}"
        return phone
    except (ValueError, TypeError):
        return phone


@register.filter
def status_badge(status):
    """Return badge color for order status"""
    status_colors = {
        'pending': 'warning',
        'processing': 'info',
        'shipped': 'primary',
        'delivered': 'success',
        'cancelled': 'danger',
        'draft': 'secondary',
        'published': 'success',
        'out_of_stock': 'danger',
    }
    return status_colors.get(status, 'secondary')

