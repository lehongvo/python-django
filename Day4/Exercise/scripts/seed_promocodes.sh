#!/bin/bash

# Seed promo codes
# This script creates promo codes in the database

set -e

# Default values
COUNT=1000
LENGTH=12

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --count)
            COUNT="$2"
            shift 2
            ;;
        --length)
            LENGTH="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [--count N] [--length N]"
            echo ""
            echo "Options:"
            echo "  --count N     Number of promo codes to create (default: 1000)"
            echo "  --length N    Length of promo codes (default: 12)"
            echo "  --help        Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}🎟️  Seeding Promo Codes${NC}"
echo "================================"
echo "Count: $COUNT"
echo "Length: $LENGTH"
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

# Verify PromoCode model exists
echo "🔍 Verifying PromoCode model..."
MODEL_CHECK=$(docker-compose exec -T web python manage.py shell -c "
from store.models import PromoCode
print('OK')
" 2>&1)

if ! echo "$MODEL_CHECK" | grep -q "OK"; then
    echo -e "${RED}❌ PromoCode model not found${NC}"
    echo "$MODEL_CHECK"
    exit 1
fi

echo -e "${GREEN}✅ PromoCode model verified${NC}"
echo ""

echo -e "${BLUE}📦 Creating promo codes...${NC}"

# Run seed command
docker-compose exec -T web python manage.py seed_promocodes --count $COUNT --length $LENGTH

echo ""
echo -e "${BLUE}📊 Verifying seeded data...${NC}"

# Verify results
VERIFY_OUTPUT=$(docker-compose exec -T web python manage.py shell -c "
from store.models import PromoCode
total = PromoCode.objects.count()
unused = PromoCode.objects.filter(is_used=False).count()
used = PromoCode.objects.filter(is_used=True).count()
print(f'Total promo codes: {total}')
print(f'Unused: {unused}')
print(f'Used: {used}')
" 2>&1)

echo "$VERIFY_OUTPUT" | while IFS= read -r line; do
    if echo "$line" | grep -q "Total promo codes:"; then
        COUNT=$(echo "$line" | awk '{print $4}')
        if [ "$COUNT" -gt 0 ]; then
            echo -e "  ${GREEN}✅${NC} $line"
        else
            echo -e "  ${RED}❌${NC} $line"
        fi
    else
        echo "  $line"
    fi
done

echo ""
echo -e "${GREEN}✅ Promo codes seeding completed!${NC}"

