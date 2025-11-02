#!/bin/bash

# Ensure all users have promo codes
# This script ensures each user has at least 10 promo codes

set -e

# Default values
SEND_EMAIL=0
BATCH_SIZE=200

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --send-email)
            SEND_EMAIL=1
            shift
            ;;
        --batch-size)
            BATCH_SIZE="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [--send-email] [--batch-size N]"
            echo ""
            echo "Options:"
            echo "  --send-email      Send email to users when codes are assigned"
            echo "  --batch-size N    Number of users to process per batch (default: 200)"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}🎁 Ensuring Users Have Promo Codes${NC}"
echo "================================"
echo "Send email: $([ "$SEND_EMAIL" = "1" ] && echo "Yes" || echo "No")"
echo "Batch size: $BATCH_SIZE"
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

# Verify models exist
echo "🔍 Verifying models..."
MODEL_CHECK=$(docker-compose exec -T web python manage.py shell -c "
from django.contrib.auth.models import User
from store.models import PromoCode
print('OK')
" 2>&1)

if ! echo "$MODEL_CHECK" | grep -q "OK"; then
    echo -e "${RED}❌ Models not found${NC}"
    echo "$MODEL_CHECK"
    exit 1
fi

echo -e "${GREEN}✅ Models verified${NC}"

# Check user count
USER_COUNT=$(docker-compose exec -T web python manage.py shell -c "
from django.contrib.auth.models import User
print(User.objects.count())
" 2>&1 | tail -1)

if [ "$USER_COUNT" = "0" ]; then
    echo -e "${YELLOW}⚠️  No users found in database${NC}"
    echo "   This script will run but won't assign any codes"
else
    echo -e "${GREEN}✅ Found $USER_COUNT user(s)${NC}"
fi

# Check available promo codes
PROMO_COUNT=$(docker-compose exec -T web python manage.py shell -c "
from store.models import PromoCode
print(PromoCode.objects.filter(is_used=False).count())
" 2>&1 | tail -1)

if [ "$PROMO_COUNT" = "0" ]; then
    echo -e "${YELLOW}⚠️  No unused promo codes available${NC}"
    echo "   Consider running seed_promocodes.sh first"
else
    echo -e "${GREEN}✅ Found $PROMO_COUNT unused promo code(s)${NC}"
fi

echo ""
echo -e "${BLUE}📦 Processing users...${NC}"

# Build command
CMD="python manage.py ensure_promos --batch-size $BATCH_SIZE"
if [ "$SEND_EMAIL" = "1" ]; then
    CMD="$CMD --send-email 1"
fi

# Run command
docker-compose exec -T web $CMD

echo ""
echo -e "${GREEN}✅ Promo code assignment completed!${NC}"

