from django.core.management.base import BaseCommand
from django.db import transaction
from store.models import PromoCode
import secrets
import string
import random


def generate_code(length: int = 12) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


class Command(BaseCommand):
    help = 'Seed random promo codes'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=1000, help='Number of promo codes to create')
        parser.add_argument('--length', type=int, default=12, help='Promo code length')

    def handle(self, *args, **options):
        count = int(options['count'])
        length = int(options['length'])

        self.stdout.write(self.style.NOTICE(f'Creating {count} promo codes (length={length})...'))

        created = 0
        batch = []
        existing = set(PromoCode.objects.values_list('promo_code', flat=True))

        while created < count:
            code = generate_code(length)
            if code in existing:
                continue
            existing.add(code)
            batch.append(PromoCode(promo_code=code, is_used=False, promo_amount=random.randint(10, 20)))
            if len(batch) >= 500:
                with transaction.atomic():
                    PromoCode.objects.bulk_create(batch, ignore_conflicts=True)
                created += len(batch)
                batch = []

        if batch:
            with transaction.atomic():
                PromoCode.objects.bulk_create(batch, ignore_conflicts=True)
            created += len(batch)

        self.stdout.write(self.style.SUCCESS(f'Done. Created {created} promo codes.'))


