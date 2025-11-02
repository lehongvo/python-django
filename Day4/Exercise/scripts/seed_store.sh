#!/bin/bash

# Seed store data (Categories, Products, Tags)
# This script seeds categories, products, and tags with optional images

set -e

# Default values
CATEGORIES=20
PRODUCTS=500
WITH_IMAGES=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
        --images)
            WITH_IMAGES=true
            shift
            ;;
        --help)
            echo "Usage: $0 [--categories N] [--products N] [--images]"
            echo ""
            echo "Options:"
            echo "  --categories N    Number of categories to create (default: 20)"
            echo "  --products N      Number of products to create (default: 500)"
            echo "  --images          Download images for products"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}🌱 Seeding Store Data${NC}"
echo "================================"
echo "Categories: $CATEGORIES"
echo "Products: $PRODUCTS"
echo "Download images: $WITH_IMAGES"
echo ""

# Check schema first
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -f "$SCRIPT_DIR/check_schema.sh" ]; then
    bash "$SCRIPT_DIR/check_schema.sh"
else
    echo -e "${YELLOW}⚠️  Schema check script not found, skipping...${NC}"
fi

# Check if docker-compose is running
if ! docker-compose ps | grep -q "exercise-web-1.*Up"; then
    echo -e "${RED}❌ Docker containers are not running${NC}"
    exit 1
fi

# Build command
SEED_CMD="python manage.py seed_store --categories $CATEGORIES --products $PRODUCTS"
if [ "$WITH_IMAGES" = true ]; then
    SEED_CMD="$SEED_CMD --images"
fi

echo -e "${BLUE}📦 Starting seed process...${NC}"
echo ""

# Run seed command
if [ "$WITH_IMAGES" = true ]; then
    echo -e "${YELLOW}⏳ This may take a while due to image downloads...${NC}"
fi

docker-compose exec -T web $SEED_CMD

echo ""
echo -e "${BLUE}📊 Verifying seeded data...${NC}"

# Verify results
VERIFY_OUTPUT=$(docker-compose exec -T web python manage.py shell -c "
from store.models import Category, Product, Tag
cat_count = Category.objects.count()
prod_count = Product.objects.count()
tag_count = Tag.objects.count()
prod_with_images = Product.objects.exclude(image='').exclude(image__isnull=True).count()
print(f'Categories: {cat_count}')
print(f'Products: {prod_count}')
print(f'Tags: {tag_count}')
print(f'Products with images: {prod_with_images}')
" 2>&1)

echo "$VERIFY_OUTPUT" | while IFS= read -r line; do
    if echo "$line" | grep -q "Categories:"; then
        COUNT=$(echo "$line" | awk '{print $2}')
        if [ "$COUNT" -gt 0 ]; then
            echo -e "  ${GREEN}✅${NC} $line"
        else
            echo -e "  ${RED}❌${NC} $line"
        fi
    elif echo "$line" | grep -q "Products:"; then
        COUNT=$(echo "$line" | awk '{print $2}')
        if [ "$COUNT" -gt 0 ]; then
            echo -e "  ${GREEN}✅${NC} $line"
        else
            echo -e "  ${RED}❌${NC} $line"
        fi
    elif echo "$line" | grep -q "Tags:"; then
        COUNT=$(echo "$line" | awk '{print $2}')
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
echo -e "${GREEN}✅ Store seeding completed!${NC}"

