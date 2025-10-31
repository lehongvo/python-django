from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import models

from store.models import PromoCode
from store.utils import claim_unused_promos, assign_welcome_promo_and_email


class Command(BaseCommand):
    help = (
        "Ensure each user has at least 10 promo codes. If a user has 0, "
        "mint/assign 10. If a user has <10, top up to 10. Optionally send email."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--send-email",
            type=int,
            default=0,
            help="1 to email users when codes are assigned or topped up to 10",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=200,
            help="Number of users to process per batch (for very large user tables)",
        )

    def handle(self, *args, **options):
        send_email = int(options.get("send_email") or 0) == 1
        batch_size = int(options.get("batch_size") or 200)

        processed = 0
        updated_users = 0

        qs = User.objects.all().order_by("id").only("id", "email", "username")
        # Process in batches to keep memory low
        start = 0
        total = qs.count()
        while start < total:
            batch = qs[start : start + batch_size]
            # Preload promo counts for this batch
            user_id_to_count = {}
            counts = (
                PromoCode.objects.filter(user_id__in=[u.id for u in batch])
                .values("user_id")
                .annotate(c=models.Count("id"))
            )
            for row in counts:
                user_id_to_count[row["user_id"]] = row["c"]

            for user in batch:
                processed += 1
                count = int(user_id_to_count.get(user.id, 0) or 0)
                if count <= 0:
                    # Assign 10 codes to users with none
                    if send_email:
                        assign_welcome_promo_and_email(user, count=10)
                    else:
                        claim_unused_promos(user, 10)
                    updated_users += 1
                elif count < 10:
                    # Top up to 10 codes for users with some but not enough
                    missing = 10 - count
                    if send_email:
                        # claim first, then email with all codes
                        claim_unused_promos(user, missing)
                        assign_welcome_promo_and_email(user, count=10)
                    else:
                        claim_unused_promos(user, missing)
                    updated_users += 1

            start += batch_size

        self.stdout.write(
            self.style.SUCCESS(
                f"Processed {processed} users — assigned codes to {updated_users} users"
            )
        )


