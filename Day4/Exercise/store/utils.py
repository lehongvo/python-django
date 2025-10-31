from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db import transaction
from typing import Optional, List, Tuple
import logging
import random
import string

# Dedicated logger for email/promo flows
logger = logging.getLogger('store.email')


def assign_welcome_promo_and_email(user, count: int = 1) -> Optional[str]:
    """Assign one or more unused promo codes to the given user and email them.
    Returns the first promo code string if assigned, else None.
    """
    from .models import PromoCode

    logger.info("assign_welcome_promo:start user=%s email=%s", getattr(user, 'username', None), getattr(user, 'email', None))

    # If user already has at least one, reuse the most recent for return value
    existing = getattr(user, 'promo_codes', None)
    if existing and existing.exists():
        code_obj = existing.order_by('-created_at').first()
        promo = code_obj.promo_code
        discount = code_obj.promo_amount
        logger.info("assign_welcome_promo:reuse code=%s amount=%s%% user_id=%s", promo, discount, getattr(user, 'id', None))
    else:
        from .models import PromoCode
        def _gen_codes(n: int) -> List[Tuple[str, float]]:
            created: List[Tuple[str, float]] = []
            for _ in range(max(0, n)):
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
                amount = random.randint(10, 20)
                try:
                    obj = PromoCode.objects.create(promo_code=code, promo_amount=amount, user=user)
                    created.append((obj.promo_code, float(obj.promo_amount)))
                except Exception:
                    # Retry with another code in case of collision
                    continue
            return created

        with transaction.atomic():
            assign_qs = (
                PromoCode.objects.select_for_update(skip_locked=True)
                .filter(user__isnull=True)
                .order_by('created_at')[: max(1, int(count))]
            )
            assigned: List[Tuple[str, float]] = []
            for code in assign_qs:
                code.user = user
                code.save(update_fields=['user'])
                assigned.append((code.promo_code, float(code.promo_amount)))
            if len(assigned) < max(1, int(count)):
                needed = max(1, int(count)) - len(assigned)
                assigned.extend(_gen_codes(needed))
            if not assigned:
                logger.warning("assign_welcome_promo:no_codes_available user_id=%s", getattr(user, 'id', None))
                return None
            # first code used as return
            promo, discount = assigned[0]
            logger.info("assign_welcome_promo:assigned batch=%s user_id=%s", len(assigned), getattr(user, 'id', None))
            assigned_codes = assigned

    # Send welcome email with the promo code
    try:
        if not getattr(user, 'email', None):
            logger.warning("assign_welcome_promo:skip_email missing_user_email code=%s user_id=%s", promo, getattr(user, 'id', None))
            return promo
        # Build promos list for email (include all codes if newly assigned; otherwise include most recent only)
        try:
            assigned_list = assigned_codes  # type: ignore[name-defined]
        except Exception:
            assigned_list = [(promo, float(discount))]
        context = {
            'user': user,
            'promo_code': promo,  # first code for backwards compatibility
            'discount': discount,
            'promos': [{'code': c, 'amount': a} for c, a in assigned_list],
        }
        subject = 'Welcome to TechStore — Your personal promo code inside'
        text_body = render_to_string('emails/welcome_promo.txt', context)
        html_body = render_to_string('emails/welcome_promo.html', context)
        msg = EmailMultiAlternatives(subject, text_body, to=[user.email] if user.email else [])
        msg.attach_alternative(html_body, 'text/html')
        sent = msg.send(fail_silently=True)
        logger.info("assign_welcome_promo:email_sent result=%s to=%s code=%s", sent, getattr(user, 'email', None), promo)
    except Exception:
        logger.exception("assign_welcome_promo:email_error to=%s code=%s", getattr(user, 'email', None), promo)

    return promo


def claim_unused_promos(user, count: int) -> int:
    """Assign 'count' unused promo codes to user without sending email.
    Returns how many were assigned.
    """
    from .models import PromoCode
    assigned_count = 0
    if count <= 0:
        return 0
    try:
        with transaction.atomic():
            pool = (
                PromoCode.objects.select_for_update(skip_locked=True)
                .filter(user__isnull=True)
                .order_by('created_at')[: int(count)]
            )
            for code in pool:
                code.user = user
                code.save(update_fields=['user'])
                assigned_count += 1
            # Mint more codes if pool was insufficient
            if assigned_count < count:
                needed = count - assigned_count
                for _ in range(needed):
                    try:
                        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
                        amount = random.randint(10, 20)
                        PromoCode.objects.create(promo_code=code, promo_amount=amount, user=user)
                        assigned_count += 1
                    except Exception:
                        continue
    except Exception:
        logger.exception("claim_unused_promos:error user_id=%s", getattr(user, 'id', None))
    return assigned_count


