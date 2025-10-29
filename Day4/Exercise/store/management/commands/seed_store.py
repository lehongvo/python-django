import random
import string
from typing import List

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.db import transaction

from store.models import Category, Tag, Product
from django.core.files.base import ContentFile
import requests


WORDS = (
    "Ultra", "Pro", "Max", "Air", "Plus", "Go", "Lite", "Smart", "Prime", "Edge",
    "Next", "Vision", "Core", "Sense", "Power", "Flex", "Hyper", "Neo", "X", "S",
)

NOUNS = (
    "Headphones", "Speaker", "Laptop", "Phone", "Watch", "Monitor", "Camera", "Router",
    "Keyboard", "Mouse", "Drone", "Vacuum", "Toothbrush", "Mixer", "Kettle", "Projector",
    "Printer", "SSD", "HDD", "Microphone",
)

# Category-specific product names for better image matching
CATEGORY_PRODUCTS = {
    "Electronics": ["Headphones", "Speaker", "Camera", "Drone", "Microphone"],
    "Computers & Laptops": ["Laptop", "Keyboard", "Mouse", "Monitor", "SSD", "HDD"],
    "Phones & Accessories": ["Phone", "Watch", "Headphones"],
    "Home & Kitchen": ["Vacuum", "Toothbrush", "Mixer", "Kettle", "Projector"],
    "Appliances": ["Vacuum", "Mixer", "Kettle", "Printer"],
    "Sports & Fitness": ["Watch", "Headphones"],
    "Beauty & Personal Care": ["Toothbrush", "Watch"],
    "Health & Wellness": ["Toothbrush", "Watch"],
    "Office & Stationery": ["Printer", "Keyboard", "Mouse"],
}

# Unsplash image IDs for different product types
PRODUCT_IMAGES = {
    "Headphones": "headphone", "Speaker": "speaker", "Laptop": "laptop", 
    "Phone": "smartphone", "Watch": "watch", "Monitor": "monitor",
    "Camera": "camera", "Router": "router", "Keyboard": "keyboard",
    "Mouse": "mouse", "Drone": "drone", "Vacuum": "vacuum",
    "Toothbrush": "toothbrush", "Mixer": "mixer", "Kettle": "kettle",
    "Projector": "projector", "Printer": "printer", "SSD": "ssd",
    "HDD": "hard drive", "Microphone": "microphone",
}

DESCRIPTIONS = (
    "Premium performance with modern design.",
    "Engineered for speed, reliability, and comfort.",
    "Crafted with high-quality materials for everyday use.",
    "Advanced features packed in a compact form factor.",
    "Seamless connectivity and long-lasting battery life.",
    "Crystal-clear display and immersive sound experience.",
    "Designed for creators, gamers, and professionals.",
)


def random_name(category_name=None) -> str:
    """Generate a random product name, optionally matching category products."""
    word1 = random.choice(WORDS)
    word2 = random.choice(WORDS)
    
    # Use category-specific products if available
    if category_name and category_name in CATEGORY_PRODUCTS:
        noun = random.choice(CATEGORY_PRODUCTS[category_name])
    else:
        noun = random.choice(NOUNS)
    
    # Avoid repeated words
    if word1 == word2:
        word2 = random.choice([w for w in WORDS if w != word1])
    
    return f"{word1} {word2} {noun}".replace("  ", " ")


def random_sentence() -> str:
    return f"{random.choice(DESCRIPTIONS)} {random.choice(DESCRIPTIONS)}"


def get_product_image_url(product_name):
    """Get a relevant Unsplash image URL for a product name."""
    # Extract the last word (the product type)
    words = product_name.split()
    product_type = words[-1] if words else "product"
    
    # Check if we have a specific image for this product type
    search_term = PRODUCT_IMAGES.get(product_type, product_type.lower())
    
    # Use Unsplash Source API for better product-specific images
    return f"https://source.unsplash.com/800x600/?{search_term}"


def unique_slug(base: str) -> str:
    base_slug = slugify(base)[:45] or "item"
    suffix = "-" + "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return (base_slug + suffix)[:60]


def ensure_tags() -> List[Tag]:
    tag_names = ["bestseller", "new", "limited", "discount", "eco", "pro"]
    tags: List[Tag] = []
    for name in tag_names:
        slug = slugify(name)
        tag, created = Tag.objects.get_or_create(slug=slug, defaults={"name": name})
        if not created and tag.name != name:
            tag.name = name
            tag.save(update_fields=["name"])
        tags.append(tag)
    return tags


class Command(BaseCommand):
    help = "Seed categories and products for the store"

    def add_arguments(self, parser):
        parser.add_argument("--categories", type=int, default=20)
        parser.add_argument("--products", type=int, default=2000)
        parser.add_argument("--images", action="store_true", help="Download random images for products")

    @transaction.atomic
    def handle(self, *args, **options):
        num_categories = int(options["categories"])
        num_products = int(options["products"])
        with_images = bool(options.get("images"))

        self.stdout.write(self.style.NOTICE(f"Seeding {num_categories} categories and {num_products} products..."))

        # Categories (real-world names)
        DEFAULT_CATEGORY_NAMES = [
            "Electronics",
            "Computers & Laptops",
            "Phones & Accessories",
            "Home & Kitchen",
            "Appliances",
            "Sports & Fitness",
            "Beauty & Personal Care",
            "Health & Wellness",
            "Baby",
            "Toys & Games",
            "Books & Media",
            "Fashion Men",
            "Fashion Women",
            "Shoes",
            "Watches & Jewelry",
            "Automotive",
            "Garden & Outdoor",
            "Pet Supplies",
            "Office & Stationery",
            "Grocery & Gourmet",
        ]

        desired_names = DEFAULT_CATEGORY_NAMES[:num_categories]
        categories: List[Category] = []
        for i, desired in enumerate(desired_names):
            desired_slug = slugify(desired)
            # Prefer existing by slug/name
            cat = Category.objects.filter(slug=desired_slug).first()
            if not cat:
                # Try converting legacy "Category i" to real name
                legacy = Category.objects.filter(name=f"Category {i+1}").first()
                if legacy:
                    legacy.name = desired
                    legacy.slug = desired_slug
                    legacy.description = legacy.description or random_sentence()
                    legacy.is_active = True
                    legacy.save()
                    cat = legacy
            if not cat:
                cat, _ = Category.objects.get_or_create(
                    name=desired,
                    defaults={
                        "slug": desired_slug,
                        "description": random_sentence(),
                        "parent": None,
                        "is_active": True,
                    },
                )
            categories.append(cat)

        tags = ensure_tags()

        # Products
        created = 0
        for i in range(num_products):
            category = random.choice(categories)
            name = random_name(category.name)
            price = round(random.uniform(9.99, 2499.99), 2)
            compare_price = price + round(random.uniform(0, 500), 2) if random.random() < 0.35 else None
            stock = random.randint(0, 200)

            slug = unique_slug(name)
            unique_sku = (slug.replace('-', '').upper()[:8] + '-' + ''.join(random.choices(string.digits, k=8)))
            product, was_created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "description": random_sentence() + "\n\n" + random_sentence(),
                    "short_description": random_sentence(),
                    "price": price,
                    "compare_price": compare_price,
                    "stock": stock,
                    "sku": unique_sku,
                    "category": category,
                    "status": "published" if stock > 0 else "out_of_stock",
                    "is_featured": random.random() < 0.1,
                },
            )
            if was_created:
                # assign random tags
                chosen = random.sample(tags, k=random.randint(0, min(3, len(tags))))
                if chosen:
                    product.tags.add(*chosen)
                created += 1

                # optionally attach a real image matching the product type
                if with_images and not getattr(product, 'image', None):
                    try:
                        # Use product-specific image URL
                        img_url = get_product_image_url(product.name)
                        resp = requests.get(img_url, timeout=15)
                        if resp.status_code == 200:
                            product.image.save(f"{slug}.jpg", ContentFile(resp.content), save=True)
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"  → Could not download image for {product.name}: {e}"))

        # Backfill images for existing products without images
        if with_images:
            missing = Product.objects.filter(image="") | Product.objects.filter(image__isnull=True)
            for p in missing:
                try:
                    # Use product-specific image URL
                    img_url = get_product_image_url(p.name)
                    resp = requests.get(img_url, timeout=15)
                    if resp.status_code == 200:
                        p.image.save(f"{p.slug}.jpg", ContentFile(resp.content), save=True)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  → Could not download image for {p.name}: {e}"))
                    continue

            if (i + 1) % 250 == 0:
                self.stdout.write(self.style.SUCCESS(f"  → Created {created} / {i+1} attempted"))

        self.stdout.write(self.style.SUCCESS("Seeding completed."))


