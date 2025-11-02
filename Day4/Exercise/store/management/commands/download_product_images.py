"""
Download images for products that don't have images yet
"""
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from store.models import Product
from django.utils.text import slugify
import requests
import urllib.parse
import logging
import json
import os

logger = logging.getLogger(__name__)

# Unsplash image IDs for different product types (same as seed_store.py)
PRODUCT_IMAGES = {
    "Headphones": "headphone", "Speaker": "speaker", "Laptop": "laptop", 
    "Phone": "smartphone", "Watch": "watch", "Monitor": "monitor",
    "Camera": "camera", "Router": "router", "Keyboard": "keyboard",
    "Mouse": "mouse", "Drone": "drone", "Vacuum": "vacuum",
    "Toothbrush": "toothbrush", "Mixer": "mixer", "Kettle": "kettle",
    "Projector": "projector", "Printer": "printer", "SSD": "ssd",
    "HDD": "hard drive", "Microphone": "microphone",
}


def load_overrides() -> dict:
    """Load per-product image overrides from seed_assets/product_image_overrides.json if present."""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        json_path = os.path.join(base_dir, "store", "seed_assets", "product_image_overrides.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


PRODUCT_IMAGE_OVERRIDES = load_overrides()


def build_keywords(product_name: str) -> str:
    name = product_name.lower()
    # Prefer brand + model if present (e.g., 'iphone 16 pro')
    for brand in ["iphone", "ipad", "macbook", "imac", "apple watch", "galaxy", "samsung", "pixel", "xiaomi", "oppo", "vivo", "sony", "canon", "nikon", "lenovo", "asus", "dell", "hp", "logitech", "anker"]:
        if brand in name:
            return name
    # Fallback to product type mapping
    words = product_name.split()
    product_type = words[-1] if words else "product"
    return PRODUCT_IMAGES.get(product_type, product_type.lower())


def get_product_image_url(product_name: str, slug: str = None) -> str:
    """Return a best-effort image URL for the given product name.
    Priority:
      1) Exact override in product_image_overrides.json (key contains name)
      2) Keyword-based image from LoremFlickr (stable via lock)
      3) Picsum seed as last resort
    """
    # 1) Exact override (substring match, case-insensitive)
    lower = product_name.lower()
    for key, url in PRODUCT_IMAGE_OVERRIDES.items():
        if key.lower() in lower and isinstance(url, str) and url.startswith("http"):
            return url

    # 2) Keyword-based provider (no API key)
    keywords = build_keywords(product_name)
    lock = slug or slugify(product_name)
    return f"https://loremflickr.com/800/600/{requests.utils.quote(keywords)}?lock={lock}"


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
                img_url = get_product_image_url(product.name, product.slug)
                headers = {"User-Agent": "TechStoreSeeder/1.0"}
                resp = requests.get(img_url, timeout=15, headers=headers)
                
                if resp.status_code == 200 and len(resp.content) > 1000:  # Check if we got actual image data
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
                    if i % 100 == 0:
                        self.stdout.write(
                            self.style.WARNING(
                                f"  ⚠️  Progress: {i}/{len(products)} ({downloaded} downloaded, {failed} failed)"
                            )
                        )
            except Exception as e:
                failed += 1
                if i % 100 == 0:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ⚠️  Progress: {i}/{len(products)} ({downloaded} downloaded, {failed} failed) - Error: {str(e)[:50]}"
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

