"""
Seed realistic categories and products that match real-world e-commerce data
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from django.core.files.base import ContentFile
from store.models import Category, Product, Tag
import random
import logging
import requests

# Disable verbose logging during seed
logging.getLogger('store.email').setLevel(logging.WARNING)


# Real-world categories with realistic product names
REALISTIC_CATEGORIES = {
    "Electronics": {
        "products": [
            "iPhone 15 Pro Max", "Samsung Galaxy S24 Ultra", "iPad Pro 12.9", 
            "MacBook Pro M3", "Dell XPS 15", "HP Spectre x360",
            "Sony WH-1000XM5 Headphones", "AirPods Pro 2", "Bose QuietComfort 45",
            "Samsung 55-inch 4K TV", "LG OLED 65-inch", "Sony Bravia 75-inch",
            "Canon EOS R6 Mark II", "Nikon D850", "Sony Alpha A7 IV",
            "Apple Watch Series 9", "Samsung Galaxy Watch 6", "Fitbit Charge 6",
            "PlayStation 5", "Xbox Series X", "Nintendo Switch OLED",
            "DJI Mavic 3 Pro", "GoPro Hero 12", "Insta360 X3"
        ]
    },
    "Computers & Laptops": {
        "products": [
            "MacBook Air M2", "MacBook Pro 16-inch M3", "Dell XPS 13",
            "HP Envy 15", "Lenovo ThinkPad X1", "ASUS ROG Strix G16",
            "Microsoft Surface Laptop 5", "Acer Predator Helios", "Razer Blade 15",
            "Gaming Desktop RTX 4090", "Workstation PC Intel i9", "Mini PC Intel NUC",
            "Mechanical Keyboard RGB", "Gaming Mouse Wireless", "4K Monitor 32-inch",
            "External SSD 2TB", "NAS Storage 8TB", "USB-C Hub Multiport"
        ]
    },
    "Phones & Accessories": {
        "products": [
            "iPhone 14", "iPhone 13 Pro", "Samsung Galaxy S23",
            "Google Pixel 8 Pro", "OnePlus 12", "Xiaomi 13 Ultra",
            "Phone Case Leather", "Screen Protector Tempered Glass", "Wireless Charger",
            "Power Bank 20000mAh", "Car Phone Mount", "Bluetooth Car Adapter",
            "Phone Stand Adjustable", "Camera Lens Kit", "Selfie Stick Tripod"
        ]
    },
    "Home & Kitchen": {
        "products": [
            "Coffee Maker Espresso", "Air Fryer 6QT", "Instant Pot Duo",
            "Stand Mixer KitchenAid", "Food Processor 14-cup", "Blender Vitamix",
            "Robot Vacuum iRobot", "Air Purifier HEPA", "Smart Thermostat Nest",
            "Dyson V15 Vacuum", "Steam Mop Bissell", "Water Filter Pitcher",
            "Knife Set 15-piece", "Cookware Set Non-Stick", "Baking Sheet Set"
        ]
    },
    "Appliances": {
        "products": [
            "Refrigerator French Door", "Washing Machine Front Load", "Dryer Electric",
            "Dishwasher Built-in", "Microwave Convection", "Oven Range Gas",
            "Water Heater Tankless", "Garbage Disposal", "Range Hood Ducted",
            "Dehumidifier 50-pint", "Portable AC Unit", "Ceiling Fan with Light"
        ]
    },
    "Fashion Men": {
        "products": [
            "Men's Leather Jacket", "Slim Fit Dress Shirt", "Chinos Pants Classic",
            "Denim Jeans Straight Fit", "Oxford Dress Shoes", "Casual Sneakers",
            "Wool Overcoat", "Suit 2-Piece Navy", "Leather Belt Genuine",
            "Watch Leather Strap", "Sunglasses Aviator", "Wallet RFID Blocking"
        ]
    },
    "Fashion Women": {
        "products": [
            "Women's Blazer Classic", "Maxi Dress Floral", "High Heels Pumps",
            "Handbag Leather Tote", "Crossbody Bag Small", "Wool Coat Long",
            "Leggings High-Waist", "Blouse Silk Sleeveless", "Boots Ankle Leather",
            "Jewelry Set Gold", "Scarf Cashmere", "Sunglasses Cat-Eye"
        ]
    },
    "Sports & Fitness": {
        "products": [
            "Yoga Mat Premium", "Dumbbells Adjustable", "Resistance Bands Set",
            "Running Shoes Men", "Fitness Tracker Garmin", "Protein Powder Whey",
            "Bicycle Mountain 21-Speed", "Treadmill Foldable", "Elliptical Machine",
            "Basketball Official", "Tennis Racket Pro", "Golf Club Set"
        ]
    },
    "Health & Wellness": {
        "products": [
            "Massage Gun Percussion", "Weighted Blanket 20lb", "Essential Oil Diffuser",
            "Yoga Blocks Foam", "Foam Roller 36-inch", "Resistance Loop Bands",
            "Meditation Cushion", "Sleep Mask Silk", "White Noise Machine",
            "Blood Pressure Monitor", "Digital Scale Body Fat", "Water Bottle Insulated"
        ]
    },
    "Beauty & Personal Care": {
        "products": [
            "Electric Toothbrush Sonic", "Hair Dryer Ionic", "Hair Straightener Ceramic",
            "Skincare Set Complete", "Makeup Brush Set", "Perfume Eau de Parfum",
            "Face Serum Vitamin C", "Moisturizer SPF 30", "Shampoo & Conditioner Set",
            "Body Lotion Hydrating", "Nail Polish Set 12", "Beauty Mirror LED"
        ]
    },
    "Toys & Games": {
        "products": [
            "LEGO Classic Set", "Board Game Monopoly", "Puzzle 1000 Pieces",
            "Action Figure Collectible", "RC Car Remote Control", "Building Blocks Wooden",
            "Doll House 3-Story", "Train Set Electric", "Educational Toys STEM",
            "Video Game Console", "VR Headset Gaming", "Card Game Uno"
        ]
    },
    "Books & Media": {
        "products": [
            "Kindle Paperwhite", "Book Stand Adjustable", "Reading Light Clip-on",
            "Bookcase 5-Shelf", "Journal Leather Bound", "Pen Set Fountain",
            "Audiobook Subscription", "Magazine Subscription", "E-Reader Case",
            "Bookmark Magnetic", "Library Stamp", "Reading Glasses Blue Light"
        ]
    },
    "Automotive": {
        "products": [
            "Car Phone Mount Magnetic", "Dash Cam 4K", "Jump Starter Portable",
            "Tire Pressure Gauge", "Car Vacuum Cordless", "LED Headlight Bulbs",
            "Car Cover All-Weather", "Seat Covers Neoprene", "Floor Mats All-Weather",
            "OBD2 Scanner", "Emergency Kit Roadside", "Car Charger Fast"
        ]
    },
    "Garden & Outdoor": {
        "products": [
            "Garden Tool Set 6-piece", "Lawn Mower Electric", "Hose Reel Wall Mount",
            "Patio Furniture Set", "Grill Gas 4-Burner", "Outdoor String Lights",
            "Plant Pots Ceramic", "Garden Gloves Leather", "Pruning Shears Bypass",
            "Watering Can 2-Gallon", "Compost Bin Tumbling", "Garden Kneeler Pad"
        ]
    },
    "Pet Supplies": {
        "products": [
            "Dog Food Premium 30lb", "Cat Litter Clumping", "Pet Bed Orthopedic",
            "Dog Leash Retractable", "Cat Scratching Post", "Pet Carrier Airline",
            "Dog Toys Puzzle", "Cat Tree Multi-Level", "Pet Grooming Brush",
            "Automatic Feeder", "Pet Camera WiFi", "Travel Water Bowl"
        ]
    },
    "Office & Stationery": {
        "products": [
            "Office Chair Ergonomic", "Standing Desk Adjustable", "Monitor Stand Dual",
            "Desk Organizer Set", "Notebook Planner 2024", "Pen Set Ballpoint",
            "File Cabinet 2-Drawer", "Paper Shredder Cross-Cut", "Label Maker",
            "Whiteboard Magnetic", "Stapler Heavy Duty", "Letter Tray Stackable"
        ]
    },
    "Baby": {
        "products": [
            "Baby Stroller 3-in-1", "Car Seat Infant", "Baby Crib Convertible",
            "High Chair Adjustable", "Baby Monitor Video", "Diaper Bag Backpack",
            "Baby Bottles 8oz Set", "Pacifier Set 3-pack", "Baby Blanket Swaddle",
            "Baby Toys Soft", "Nursing Pillow", "Baby Carrier Ergonomic"
        ]
    },
    "Shoes": {
        "products": [
            "Running Shoes Men's", "Running Shoes Women's", "Dress Shoes Oxford",
            "Boots Ankle Leather", "Sneakers Casual", "Sandals Comfort",
            "Hiking Boots Waterproof", "Basketball Shoes High-Top", "Slippers Memory Foam",
            "Work Boots Steel Toe", "Formal Heels 3-inch", "Flats Ballerina"
        ]
    },
    "Watches & Jewelry": {
        "products": [
            "Smartwatch Fitness", "Luxury Watch Swiss", "Leather Watch Band",
            "Diamond Ring Solitaire", "Gold Necklace Chain", "Silver Bracelet",
            "Earrings Stud Diamond", "Pearl Necklace Classic", "Engagement Ring",
            "Watch Box Display", "Jewelry Organizer", "Watch Winder Automatic"
        ]
    },
    "Home Improvement": {
        "products": [
            "Power Drill Cordless", "Tool Set 200-piece", "Work Light LED",
            "Ladder Step 6-foot", "Paint Roller Kit", "Screwdriver Set Magnetic",
            "Level Tool 48-inch", "Tape Measure Laser", "Safety Glasses",
            "Work Gloves Heavy Duty", "Tool Box Rolling", "Extension Cord 50ft"
        ]
    },
    "Grocery & Gourmet": {
        "products": [
            "Coffee Beans Premium", "Organic Tea Selection", "Olive Oil Extra Virgin",
            "Honey Raw Unfiltered", "Spice Set 24-piece", "Vinegar Balsamic",
            "Chocolate Gift Box", "Gourmet Gift Basket", "Wine Set Red",
            "Kitchen Scale Digital", "Food Storage Containers", "Coffee Grinder Burr"
        ]
    }
}


class Command(BaseCommand):
    help = "Seed realistic categories and products (30 categories, 1000 products)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--categories", type=int, default=30,
            help="Number of categories to create (default: 30)"
        )
        parser.add_argument(
            "--products", type=int, default=1000,
            help="Number of products to create (default: 1000)"
        )
        parser.add_argument(
            "--images", action="store_true",
            help="Download images for products from internet"
        )

    @transaction.atomic
    def handle(self, *args, **options):
        num_categories = min(options["categories"], len(REALISTIC_CATEGORIES))
        num_products = options["products"]
        with_images = options.get("images", False)

        self.stdout.write(self.style.SUCCESS(
            f"🌱 Seeding {num_categories} realistic categories and {num_products} products..."
        ))
        if with_images:
            self.stdout.write(self.style.NOTICE("  📸 Images will be downloaded for products..."))

        # Step 1: Create Categories
        category_list = list(REALISTIC_CATEGORIES.items())[:num_categories]
        categories = []
        
        for cat_name, cat_data in category_list:
            slug = slugify(cat_name)
            category, created = Category.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": cat_name,
                    "description": f"Shop {cat_name.lower()} products at TechStore",
                    "is_active": True,
                }
            )
            if not created:
                category.is_active = True
                category.save()
            categories.append(category)
            self.stdout.write(self.style.SUCCESS(f"  ✅ Category [{len(categories)}/{num_categories}]: {cat_name}"))

        # Step 2: Create Tags
        tag_names = ["bestseller", "new", "limited", "discount", "premium", "eco-friendly"]
        tags = []
        for tag_name in tag_names:
            slug = slugify(tag_name)
            tag, _ = Tag.objects.get_or_create(
                slug=slug,
                defaults={"name": tag_name}
            )
            tags.append(tag)

        # Step 3: Create Products - distribute across categories realistically
        products_per_category = num_products // num_categories
        remaining_products = num_products % num_categories

        created_count = 0
        total_to_create = num_products

        self.stdout.write(self.style.NOTICE(f"\n📦 Creating {num_products} products across {num_categories} categories..."))
        self.stdout.write(self.style.NOTICE(f"   Progress will be shown every 50 products\n"))

        for i, (cat_name, cat_data) in enumerate(category_list):
            category = categories[i]
            
            # Get realistic product names for this category
            realistic_products = cat_data["products"]
            
            # Calculate how many products to create for this category
            products_to_create = products_per_category
            if i < remaining_products:
                products_to_create += 1

            self.stdout.write(self.style.SUCCESS(f"\n📂 Category [{i+1}/{num_categories}]: {cat_name} - Creating {products_to_create} products..."))

            category_created = 0
            for j in range(products_to_create):
                # Use realistic product names, cycling through them if needed
                base_product_name = realistic_products[j % len(realistic_products)]
                
                # Add variation to make unique
                if j >= len(realistic_products):
                    variation = f" {random.choice(['Pro', 'Plus', 'Elite', 'Premium', 'Classic', 'Deluxe'])}"
                    if random.random() < 0.3:  # Sometimes add size/color
                        variation += f" {random.choice(['Black', 'White', 'Silver', 'Gold', '32GB', '64GB', '128GB'])}"
                    product_name = base_product_name + variation
                else:
                    product_name = base_product_name

                # Generate unique slug
                base_slug = slugify(product_name)
                slug = base_slug
                counter = 1
                while Product.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                # Generate realistic price based on category
                price = self._generate_realistic_price(cat_name)
                compare_price = price * random.uniform(1.1, 1.5) if random.random() < 0.3 else None
                stock = random.randint(0, 200)

                # Generate unique SKU
                import time
                import string
                name_part = product_name.replace(' ', '').upper()[:8]
                timestamp = int(time.time() * 1000)  # Use milliseconds for better uniqueness
                random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                sku = f"{name_part}-{timestamp}-{random_suffix}"
                
                # Ensure SKU is unique
                while Product.objects.filter(sku=sku).exists():
                    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                    sku = f"{name_part}-{timestamp}-{random_suffix}"

                # Create product
                try:
                    product, was_created = Product.objects.get_or_create(
                        slug=slug,
                        defaults={
                            "name": product_name,
                            "description": f"{product_name} - High quality product from TechStore. "
                                          f"Perfect for your {cat_name.lower()} needs.",
                            "short_description": f"Premium {product_name.lower()} with excellent quality",
                            "price": round(price, 2),
                            "compare_price": round(compare_price, 2) if compare_price else None,
                            "stock": stock,
                            "category": category,
                            "status": "published" if stock > 0 else "out_of_stock",
                            "is_featured": random.random() < 0.1,
                            "sku": sku,  # Set SKU explicitly to prevent auto-generation
                        }
                    )
                except Exception as e:
                    # If get_or_create fails due to SKU conflict, try again with new SKU
                    self.stdout.write(self.style.WARNING(f"    ⚠️  Retrying product '{product_name[:40]}...' (SKU conflict)"))
                    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                    sku = f"{name_part}-{int(time.time() * 1000)}-{random_suffix}"
                    product, was_created = Product.objects.get_or_create(
                        slug=slug,
                        defaults={
                            "name": product_name,
                            "description": f"{product_name} - High quality product from TechStore. "
                                          f"Perfect for your {cat_name.lower()} needs.",
                            "short_description": f"Premium {product_name.lower()} with excellent quality",
                            "price": round(price, 2),
                            "compare_price": round(compare_price, 2) if compare_price else None,
                            "stock": stock,
                            "category": category,
                            "status": "published" if stock > 0 else "out_of_stock",
                            "is_featured": random.random() < 0.1,
                            "sku": sku,
                        }
                    )

                if was_created:
                    # Assign random tags
                    selected_tags = random.sample(tags, k=random.randint(0, min(3, len(tags))))
                    if selected_tags:
                        product.tags.add(*selected_tags)
                    
                    # Download image if requested
                    if with_images and not product.image:
                        try:
                            img_url = self._get_product_image_url(product_name, slug)
                            headers = {"User-Agent": "TechStoreSeeder/1.0"}
                            resp = requests.get(img_url, timeout=15, headers=headers)
                            if resp.status_code == 200:
                                product.image.save(f"{slug}.jpg", ContentFile(resp.content), save=True)
                        except Exception as e:
                            # Silently skip if image download fails
                            pass
                    
                    created_count += 1
                    category_created += 1

                    # Show progress every 50 products globally
                    if created_count % 50 == 0:
                        progress_pct = (created_count / total_to_create) * 100
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  📊 Global Progress: {created_count}/{total_to_create} products ({progress_pct:.1f}%)"
                            )
                        )
                    # Show category progress every 10 products in category
                    elif category_created > 0 and category_created % 10 == 0:
                        self.stdout.write(
                            self.style.NOTICE(
                                f"    → Category '{cat_name}': {category_created}/{products_to_create} products created"
                            )
                        )
            
            # Summary for each category
            if category_created > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✅ Completed '{cat_name}': {category_created} products created"
                    )
                )

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Seeding completed!"
        ))
        self.stdout.write(self.style.SUCCESS(
            f"   Categories: {Category.objects.count()}"
        ))
        self.stdout.write(self.style.SUCCESS(
            f"   Products: {Product.objects.count()}"
        ))

    def _generate_realistic_price(self, category_name):
        """Generate realistic prices based on category"""
        price_ranges = {
            "Electronics": (99, 2999),
            "Computers & Laptops": (299, 4999),
            "Phones & Accessories": (19, 1499),
            "Home & Kitchen": (29, 899),
            "Appliances": (199, 2499),
            "Fashion Men": (29, 499),
            "Fashion Women": (19, 699),
            "Sports & Fitness": (19, 1999),
            "Health & Wellness": (15, 399),
            "Beauty & Personal Care": (9, 299),
            "Toys & Games": (9, 499),
            "Books & Media": (9, 299),
            "Automotive": (19, 799),
            "Garden & Outdoor": (19, 1499),
            "Pet Supplies": (9, 299),
            "Office & Stationery": (9, 899),
            "Baby": (19, 599),
            "Shoes": (29, 499),
            "Watches & Jewelry": (49, 9999),
            "Home Improvement": (9, 599),
            "Grocery & Gourmet": (5, 299),
        }
        
        min_price, max_price = price_ranges.get(category_name, (10, 499))
        return random.uniform(min_price, max_price)

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
        import urllib.parse
        encoded_term = urllib.parse.quote(search_terms)
        return f"https://loremflickr.com/800/600/{encoded_term}?lock={hash(slug) % 1000}"

