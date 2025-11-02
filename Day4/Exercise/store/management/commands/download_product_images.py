"""
Download images for products that don't have images yet
"""
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from store.models import Product
import requests
import urllib.parse
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Download images for products that don't have images"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit", type=int, default=None,
            help="Limit number of products to process"
        )
        parser.add_argument(
            "--offset", type=int, default=0,
            help="Skip first N products"
        )

    def handle(self, *args, **options):
        limit = options.get("limit")
        offset = options.get("offset", 0)

        # Get products without images
        products_qs = Product.objects.filter(image__isnull=True) | Product.objects.filter(image="")
        total_count = products_qs.count()
        
        if limit:
            products_qs = products_qs[offset:offset+limit]
            products = list(products_qs)
        else:
            products = list(products_qs[offset:])
        
        self.stdout.write(self.style.SUCCESS(
            f"📸 Found {total_count} products without images"
        ))
        self.stdout.write(self.style.NOTICE(
            f"   Processing {len(products)} products..."
        ))

        downloaded = 0
        failed = 0

        for i, product in enumerate(products, 1):
            try:
                img_url = self._get_product_image_url(product.name, product.slug)
                headers = {"User-Agent": "TechStoreSeeder/1.0"}
                resp = requests.get(img_url, timeout=15, headers=headers)
                
                if resp.status_code == 200:
                    product.image.save(f"{product.slug}.jpg", ContentFile(resp.content), save=True)
                    downloaded += 1
                    
                    if i % 50 == 0:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  ✅ Downloaded {downloaded}/{i} images... ({failed} failed)"
                            )
                        )
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                if i % 100 == 0:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ⚠️  Progress: {i}/{len(products)} ({downloaded} downloaded, {failed} failed)"
                        )
                    )

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Completed!"
        ))
        self.stdout.write(self.style.SUCCESS(
            f"   Downloaded: {downloaded} images"
        ))
        self.stdout.write(self.style.SUCCESS(
            f"   Failed: {failed} images"
        ))

    def _get_product_image_url(self, product_name: str, slug: str) -> str:
        """Get image URL for product using LoremFlickr based on product name keywords"""
        # Extract keywords from product name
        keywords = product_name.lower()
        
        # Remove common words
        stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from']
        words = [w for w in keywords.split() if w not in stop_words and len(w) > 2]
        
        # Use first 2-3 meaningful words
        search_terms = ' '.join(words[:3]) if len(words) >= 3 else ' '.join(words[:2]) if len(words) >= 2 else keywords
        
        # Use LoremFlickr with lock for consistent images
        encoded_term = urllib.parse.quote(search_terms)
        return f"https://loremflickr.com/800/600/{encoded_term}?lock={hash(slug) % 1000}"

