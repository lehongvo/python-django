#!/bin/bash

# Master script to seed all data
# This script runs all seeding operations in the correct order

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
CATEGORIES=20
PRODUCTS=500
PROMO_COUNT=1000
WITH_IMAGES=false
SEND_EMAIL=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --categories)
            CATEGORIES="$2"
            shift 2
            ;;
        --products)
            PRODUCTS="$2"
            shift 2
            ;;
        --promo-count)
            PROMO_COUNT="$2"
            shift 2
            ;;
        --images)
            WITH_IMAGES=true
            shift
            ;;
        --send-email)
            SEND_EMAIL=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --categories N      Number of categories (default: 20)"
            echo "  --products N        Number of products (default: 500)"
            echo "  --promo-count N     Number of promo codes (default: 1000)"
            echo "  --images            Download images for products"
            echo "  --send-email        Send email when assigning promo codes"
            echo "  --help              Show this help message"
            echo ""
            echo "Example:"
            echo "  $0 --categories 20 --products 500 --images"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_DIR"

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          TechStore 2025 - Data Seeding Script               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Step 1: Check schema
echo -e "${BLUE}Step 1/4:${NC} Checking database schema..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
bash "$SCRIPT_DIR/check_schema.sh"
echo ""

# Step 2: Seed store data (Categories, Products, Tags)
echo -e "${BLUE}Step 2/4:${NC} Seeding store data..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
SEED_STORE_CMD="bash \"$SCRIPT_DIR/seed_store.sh\" --categories $CATEGORIES --products $PRODUCTS"
if [ "$WITH_IMAGES" = true ]; then
    SEED_STORE_CMD="$SEED_STORE_CMD --images"
fi
eval $SEED_STORE_CMD
echo ""

# Step 3: Seed promo codes
echo -e "${BLUE}Step 3/4:${NC} Seeding promo codes..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
bash "$SCRIPT_DIR/seed_promocodes.sh" --count $PROMO_COUNT
echo ""

# Step 4: Ensure users have promo codes
echo -e "${BLUE}Step 4/4:${NC} Ensuring users have promo codes..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ENSURE_CMD="bash \"$SCRIPT_DIR/ensure_promos.sh\""
if [ "$SEND_EMAIL" = true ]; then
    ENSURE_CMD="$ENSURE_CMD --send-email"
fi
eval $ENSURE_CMD
echo ""

# Final summary
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    Seeding Summary                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

SUMMARY=$(docker-compose exec -T web python manage.py shell -c "
from store.models import Category, Product, Tag, PromoCode
from django.contrib.auth.models import User
cat_count = Category.objects.count()
prod_count = Product.objects.count()
tag_count = Tag.objects.count()
promo_count = PromoCode.objects.count()
user_count = User.objects.count()
prod_with_images = Product.objects.exclude(image='').exclude(image__isnull=True).count()

print(f'Categories: {cat_count}')
print(f'Products: {prod_count}')
print(f'  - With images: {prod_with_images}')
print(f'Tags: {tag_count}')
print(f'Promo codes: {promo_count}')
print(f'Users: {user_count}')
" 2>&1)

echo "$SUMMARY" | while IFS= read -r line; do
    if echo "$line" | grep -q "Categories:\|Products:\|Tags:\|Promo codes:\|Users:"; then
        COUNT=$(echo "$line" | awk '{print $NF}')
        if [ "$COUNT" -gt 0 ]; then
            echo -e "  ${GREEN}✅${NC} $line"
        else
            echo -e "  ${YELLOW}⚠️${NC}  $line"
        fi
    else
        echo "  $line"
    fi
done

echo ""
echo -e "${GREEN}✨ All seeding operations completed successfully!${NC}"
echo ""
echo -e "${CYAN}Access your admin panel at:${NC}"
echo "  http://localhost:8001/admin"
echo "  Username: admin"
echo "  Password: admin123"
echo ""

