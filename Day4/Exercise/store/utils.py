from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db import transaction
from typing import Optional


def assign_welcome_promo_and_email(user) -> Optional[str]:
    """Assign an unused promo code to the given user and email it.
    Returns the promo code string if assigned, else None.
    """
    from .models import PromoCode

    # If user already has one, reuse the most recent
    existing = getattr(user, 'promo_codes', None)
    if existing and existing.exists():
        code_obj = existing.order_by('-created_at').first()
        promo = code_obj.promo_code
        discount = code_obj.promo_amount
    else:
        with transaction.atomic():
            code_obj = (
                PromoCode.objects.select_for_update(skip_locked=True)
                .filter(user__isnull=True)
                .order_by('created_at')
                .first()
            )
            if not code_obj:
                return None
            code_obj.user = user
            # Keep is_used=False until redeemed at checkout
            code_obj.save(update_fields=['user'])
            promo = code_obj.promo_code
            discount = code_obj.promo_amount

    # Send welcome email with the promo code
    try:
        context = {
            'user': user,
            'promo_code': promo,
            'discount': discount,
        }
        subject = 'Welcome to TechStore — Your personal promo code inside'
        text_body = render_to_string('emails/welcome_promo.txt', context)
        html_body = render_to_string('emails/welcome_promo.html', context)
        msg = EmailMultiAlternatives(subject, text_body, to=[user.email] if user.email else [])
        msg.attach_alternative(html_body, 'text/html')
        msg.send(fail_silently=True)
    except Exception:
        pass

    return promo


