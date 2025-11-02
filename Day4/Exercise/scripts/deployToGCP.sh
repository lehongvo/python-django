#!/bin/bash

################################################################################
# Professional Django E-commerce Deployment Script to Google Cloud Platform
# 
# This script deploys the complete Django e-commerce application stack:
# - Cloud Run (Main Application Service)
# - Cloud SQL (PostgreSQL Database)
# - Cloud Storage (Static & Media files)
# - Artifact Registry (Docker images)
# - Cloud Scheduler (Optional: Scheduled tasks)
# - Cloud Tasks (Optional: Background jobs)
#
# Usage:
#   ./deployToGCP.sh [OPTIONS]
#
# Options:
#   --project-id PROJECT_ID     GCP Project ID (required)
#   --region REGION             GCP Region (default: asia-southeast1)
#   --service-name NAME         Cloud Run service name (default: ecommerce-app)
#   --db-tier TIER              Cloud SQL tier (default: db-f1-micro)
#   --db-password PASSWORD      Database password (auto-generated if not provided)
#   --skip-db-setup             Skip Cloud SQL database setup
#   --skip-storage-setup         Skip Cloud Storage bucket setup
#   --skip-seed                  Skip database seeding
#   --auto-approve               Skip confirmation prompts
#   --help                      Show this help message
################################################################################

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "$PROJECT_DIR"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1" >&2
}

log_step() {
    echo -e "\n${CYAN}${BOLD}▶ $1${NC}"
}

# Default configuration
PROJECT_ID=""
REGION="asia-southeast1"
SERVICE_NAME="ecommerce-app"
DB_INSTANCE_NAME="ecommerce-db"
DB_NAME="ecommercedb"
DB_USER="ecommerceuser"
DB_PASSWORD=""
DB_TIER="db-f1-micro"
BUCKET_NAME_STATIC=""
BUCKET_NAME_MEDIA=""
SKIP_DB_SETUP=false
SKIP_STORAGE_SETUP=false
SKIP_SEED=false
AUTO_APPROVE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --project-id)
            PROJECT_ID="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        --service-name)
            SERVICE_NAME="$2"
            shift 2
            ;;
        --db-tier)
            DB_TIER="$2"
            shift 2
            ;;
        --db-password)
            DB_PASSWORD="$2"
            shift 2
            ;;
        --skip-db-setup)
            SKIP_DB_SETUP=true
            shift
            ;;
        --skip-storage-setup)
            SKIP_STORAGE_SETUP=true
            shift
            ;;
        --skip-seed)
            SKIP_SEED=true
            shift
            ;;
        --auto-approve)
            AUTO_APPROVE=true
            shift
            ;;
        --help)
            head -30 "$0" | tail -29
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validation functions
check_requirements() {
    log_step "Checking Requirements"
    
    local missing=0
    
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed"
        echo "Install: https://cloud.google.com/sdk/docs/install"
        missing=1
    fi
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        missing=1
    fi
    
    if ! command -v python3 &> /dev/null; then
        log_warning "python3 not found (optional for SECRET_KEY generation)"
    fi
    
    if [ $missing -eq 1 ]; then
        exit 1
    fi
    
    log_success "All requirements met"
}

validate_project() {
    if [ -z "$PROJECT_ID" ]; then
        log_warning "GCP Project ID is required"
        read -p "Enter your GCP Project ID: " PROJECT_ID
        if [ -z "$PROJECT_ID" ]; then
            log_error "Project ID cannot be empty"
            exit 1
        fi
    fi
    
    # Validate project exists and user has access
    if ! gcloud projects describe "$PROJECT_ID" &>/dev/null; then
        log_error "Project '$PROJECT_ID' not found or no access"
        exit 1
    fi
    
    log_success "Project validated: $PROJECT_ID"
}

# Setup functions
setup_gcp_project() {
    log_step "Setting up GCP Project"
    
    gcloud config set project "$PROJECT_ID"
    gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet || true
    
    log_success "GCP project configured"
}

enable_apis() {
    log_step "Enabling Required APIs"
    
    local apis=(
        "cloudbuild.googleapis.com"
        "run.googleapis.com"
        "sqladmin.googleapis.com"
        "sql-component.googleapis.com"
        "storage-api.googleapis.com"
        "secretmanager.googleapis.com"
        "artifactregistry.googleapis.com"
        "cloudscheduler.googleapis.com"
        "cloudtasks.googleapis.com"
        "logging.googleapis.com"
        "monitoring.googleapis.com"
    )
    
    for api in "${apis[@]}"; do
        log_info "Enabling $api..."
        gcloud services enable "$api" --project="$PROJECT_ID" --quiet || true
    done
    
    log_success "APIs enabled"
}

setup_database() {
    if [ "$SKIP_DB_SETUP" = true ]; then
        log_warning "Skipping database setup"
        return
    fi
    
    log_step "Setting up Cloud SQL PostgreSQL"
    
    # Generate secure password if not provided
    if [ -z "$DB_PASSWORD" ]; then
        log_info "Generating secure database password..."
        DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
        log_success "DB password generated (save this!): ${DB_PASSWORD}"
    fi
    
    # Check if instance exists
    if gcloud sql instances describe "$DB_INSTANCE_NAME" --project="$PROJECT_ID" &>/dev/null; then
        log_warning "Cloud SQL instance '$DB_INSTANCE_NAME' already exists"
        
        # Update password if provided
        if [ -n "$DB_PASSWORD" ]; then
            log_info "Updating database user password..."
            gcloud sql users set-password "$DB_USER" \
                --instance="$DB_INSTANCE_NAME" \
                --password="$DB_PASSWORD" \
                --project="$PROJECT_ID" \
                --quiet || true
        fi
    else
        log_info "Creating Cloud SQL instance (this may take 5-10 minutes)..."
        gcloud sql instances create "$DB_INSTANCE_NAME" \
            --database-version=POSTGRES_15 \
            --tier="$DB_TIER" \
            --region="$REGION" \
            --project="$PROJECT_ID" \
            --backup-start-time=03:00 \
            --maintenance-window-day=SUN \
            --maintenance-window-hour=04 \
            --quiet
        
        log_info "Setting database root password..."
        gcloud sql users set-password postgres \
            --instance="$DB_INSTANCE_NAME" \
            --password="$DB_PASSWORD" \
            --project="$PROJECT_ID" \
            --quiet
        
        # Create database
        log_info "Creating database '$DB_NAME'..."
        gcloud sql databases create "$DB_NAME" \
            --instance="$DB_INSTANCE_NAME" \
            --project="$PROJECT_ID" \
            --quiet || true
        
        # Create database user
        log_info "Creating database user '$DB_USER'..."
        gcloud sql users create "$DB_USER" \
            --instance="$DB_INSTANCE_NAME" \
            --password="$DB_PASSWORD" \
            --project="$PROJECT_ID" \
            --quiet || true
    fi
    
    # Get Cloud SQL connection details
    DB_CONNECTION_NAME=$(gcloud sql instances describe "$DB_INSTANCE_NAME" \
        --project="$PROJECT_ID" \
        --format="value(connectionName)")
    
    DB_PRIVATE_IP=$(gcloud sql instances describe "$DB_INSTANCE_NAME" \
        --project="$PROJECT_ID" \
        --format="value(ipAddresses[0].ipAddress)" 2>/dev/null || echo "")
    
    log_success "Database setup complete"
    log_info "Connection: $DB_CONNECTION_NAME"
}

setup_storage() {
    if [ "$SKIP_STORAGE_SETUP" = true ]; then
        log_warning "Skipping storage setup"
        return
    fi
    
    log_step "Setting up Cloud Storage Buckets"
    
    # Set bucket names
    if [ -z "$BUCKET_NAME_STATIC" ]; then
        BUCKET_NAME_STATIC="${PROJECT_ID}-static-$(date +%s | tail -c 6)"
    fi
    if [ -z "$BUCKET_NAME_MEDIA" ]; then
        BUCKET_NAME_MEDIA="${PROJECT_ID}-media-$(date +%s | tail -c 6)"
    fi
    
    # Create static bucket
    if gsutil ls -b "gs://${BUCKET_NAME_STATIC}" &>/dev/null; then
        log_warning "Bucket '$BUCKET_NAME_STATIC' already exists"
    else
        log_info "Creating static files bucket..."
        gsutil mb -p "$PROJECT_ID" -l "$REGION" -c STANDARD "gs://${BUCKET_NAME_STATIC}"
        gsutil iam ch allUsers:objectViewer "gs://${BUCKET_NAME_STATIC}"
        gsutil web set -m index.html -e 404.html "gs://${BUCKET_NAME_STATIC}" 2>/dev/null || true
        
        # Set CORS if cors.json exists
        if [ -f "$PROJECT_DIR/cors.json" ]; then
            gsutil cors set "$PROJECT_DIR/cors.json" "gs://${BUCKET_NAME_STATIC}"
        fi
    fi
    
    # Create media bucket
    if gsutil ls -b "gs://${BUCKET_NAME_MEDIA}" &>/dev/null; then
        log_warning "Bucket '$BUCKET_NAME_MEDIA' already exists"
    else
        log_info "Creating media files bucket..."
        gsutil mb -p "$PROJECT_ID" -l "$REGION" -c STANDARD "gs://${BUCKET_NAME_MEDIA}"
        gsutil iam ch allUsers:objectViewer "gs://${BUCKET_NAME_MEDIA}"
        
        # Set CORS if cors.json exists
        if [ -f "$PROJECT_DIR/cors.json" ]; then
            gsutil cors set "$PROJECT_DIR/cors.json" "gs://${BUCKET_NAME_MEDIA}"
        fi
    fi
    
    log_success "Storage buckets created"
}

setup_artifact_registry() {
    log_step "Setting up Artifact Registry"
    
    ARTIFACT_REGISTRY="${REGION}-docker.pkg.dev/${PROJECT_ID}/ecommerce-images"
    
    if gcloud artifacts repositories describe ecommerce-images \
        --location="$REGION" \
        --project="$PROJECT_ID" &>/dev/null; then
        log_warning "Artifact Registry repository already exists"
    else
        log_info "Creating Artifact Registry repository..."
        gcloud artifacts repositories create ecommerce-images \
            --repository-format=docker \
            --location="$REGION" \
            --project="$PROJECT_ID" \
            --quiet
    fi
    
    log_success "Artifact Registry ready"
}

build_and_push_image() {
    log_step "Building and Pushing Docker Image"
    
    IMAGE_NAME="${ARTIFACT_REGISTRY}/${SERVICE_NAME}:latest"
    IMAGE_TAG="${ARTIFACT_REGISTRY}/${SERVICE_NAME}:$(git rev-parse --short HEAD 2>/dev/null || date +%s)"
    
    log_info "Building Docker image..."
    if ! docker build -t "$IMAGE_NAME" -t "$IMAGE_TAG" .; then
        log_error "Docker build failed"
        exit 1
    fi
    
    log_info "Pushing image to Artifact Registry..."
    docker push "$IMAGE_NAME"
    docker push "$IMAGE_TAG" || true
    
    log_success "Image pushed: $IMAGE_NAME"
}

load_env_file() {
    local env_file="${PROJECT_DIR}/.env"
    if [ -f "$env_file" ]; then
        log_info "Loading environment variables from .env file..."
        
        # Parse .env file manually to handle all cases
        while IFS= read -r line || [ -n "$line" ]; do
            # Skip comments and empty lines
            [[ "$line" =~ ^[[:space:]]*# ]] && continue
            [[ -z "${line// }" ]] && continue
            [[ ! "$line" =~ = ]] && continue
            
            # Extract key and value
            key=$(echo "$line" | cut -d '=' -f1 | xargs)
            value=$(echo "$line" | cut -d '=' -f2- | xargs)
            
            # Remove quotes if present
            value=$(echo "$value" | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")
            
            # Export variable
            export "${key}=${value}"
        done < "$env_file"
        
        log_success "Environment variables loaded from .env"
    else
        log_warning ".env file not found, using defaults or prompts"
    fi
}

get_environment_vars() {
    log_step "Collecting Environment Variables"
    
    # Load .env file if it exists
    load_env_file
    
    # Generate SECRET_KEY if not provided
    if [ -z "${SECRET_KEY:-}" ]; then
        if command -v python3 &> /dev/null; then
            SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null)
        else
            SECRET_KEY=$(openssl rand -base64 50 | tr -d "=+/" | cut -c1-50)
        fi
        log_info "Generated SECRET_KEY"
    fi
    
    # Use .env values or prompt for optional variables
    if [ "$AUTO_APPROVE" = false ] && [ -z "${EMAIL_HOST_USER:-}" ]; then
        echo ""
        read -p "Email Host User (optional, press Enter to use .env or skip): " EMAIL_HOST_USER_INPUT
        [ -n "$EMAIL_HOST_USER_INPUT" ] && EMAIL_HOST_USER="$EMAIL_HOST_USER_INPUT"
    fi
    
    if [ "$AUTO_APPROVE" = false ] && [ -z "${EMAIL_HOST_PASSWORD:-}" ]; then
        read -p "Email Host Password (optional, press Enter to use .env or skip): " EMAIL_HOST_PASSWORD_INPUT
        [ -n "$EMAIL_HOST_PASSWORD_INPUT" ] && EMAIL_HOST_PASSWORD="$EMAIL_HOST_PASSWORD_INPUT"
    fi
    
    if [ "$AUTO_APPROVE" = false ] && [ -z "${GOOGLE_CLIENT_ID:-}" ]; then
        read -p "Google Client ID (optional, press Enter to use .env or skip): " GOOGLE_CLIENT_ID_INPUT
        [ -n "$GOOGLE_CLIENT_ID_INPUT" ] && GOOGLE_CLIENT_ID="$GOOGLE_CLIENT_ID_INPUT"
    fi
    
    if [ "$AUTO_APPROVE" = false ] && [ -z "${GOOGLE_CLIENT_SECRET:-}" ]; then
        read -p "Google Client Secret (optional, press Enter to use .env or skip): " GOOGLE_CLIENT_SECRET_INPUT
        [ -n "$GOOGLE_CLIENT_SECRET_INPUT" ] && GOOGLE_CLIENT_SECRET="$GOOGLE_CLIENT_SECRET_INPUT"
    fi
    
    if [ "$AUTO_APPROVE" = false ] && [ -z "${FACEBOOK_APP_ID:-}" ]; then
        read -p "Facebook App ID (optional, press Enter to use .env or skip): " FACEBOOK_APP_ID_INPUT
        [ -n "$FACEBOOK_APP_ID_INPUT" ] && FACEBOOK_APP_ID="$FACEBOOK_APP_ID_INPUT"
    fi
    
    if [ "$AUTO_APPROVE" = false ] && [ -z "${FACEBOOK_APP_SECRET:-}" ]; then
        read -p "Facebook App Secret (optional, press Enter to use .env or skip): " FACEBOOK_APP_SECRET_INPUT
        [ -n "$FACEBOOK_APP_SECRET_INPUT" ] && FACEBOOK_APP_SECRET="$FACEBOOK_APP_SECRET_INPUT"
    fi
    
    # Build environment variables string
    ENV_VARS="SECRET_KEY=${SECRET_KEY}"
    ENV_VARS="${ENV_VARS},DEBUG=0"
    ENV_VARS="${ENV_VARS},ALLOWED_HOSTS=*"
    ENV_VARS="${ENV_VARS},DB_HOST=/cloudsql/${DB_CONNECTION_NAME}"
    ENV_VARS="${ENV_VARS},DB_NAME=${DB_NAME}"
    ENV_VARS="${ENV_VARS},DB_USER=${DB_USER}"
    ENV_VARS="${ENV_VARS},DB_PASSWORD=${DB_PASSWORD}"
    ENV_VARS="${ENV_VARS},DB_PORT=5432"
    ENV_VARS="${ENV_VARS},STATIC_URL=https://storage.googleapis.com/${BUCKET_NAME_STATIC}/"
    ENV_VARS="${ENV_VARS},MEDIA_URL=https://storage.googleapis.com/${BUCKET_NAME_MEDIA}/"
    ENV_VARS="${ENV_VARS},GS_BUCKET_NAME_STATIC=${BUCKET_NAME_STATIC}"
    ENV_VARS="${ENV_VARS},GS_BUCKET_NAME_MEDIA=${BUCKET_NAME_MEDIA}"
    
    [ -n "${EMAIL_HOST_USER:-}" ] && ENV_VARS="${ENV_VARS},EMAIL_HOST_USER=${EMAIL_HOST_USER}"
    [ -n "${EMAIL_HOST_PASSWORD:-}" ] && ENV_VARS="${ENV_VARS},EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD}"
    [ -n "${GOOGLE_CLIENT_ID:-}" ] && ENV_VARS="${ENV_VARS},GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}"
    [ -n "${GOOGLE_CLIENT_SECRET:-}" ] && ENV_VARS="${ENV_VARS},GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}"
    [ -n "${FACEBOOK_APP_ID:-}" ] && ENV_VARS="${ENV_VARS},FACEBOOK_APP_ID=${FACEBOOK_APP_ID}"
    [ -n "${FACEBOOK_APP_SECRET:-}" ] && ENV_VARS="${ENV_VARS},FACEBOOK_APP_SECRET=${FACEBOOK_APP_SECRET}"
    
    log_success "Environment variables configured"
}

deploy_cloud_run() {
    log_step "Deploying to Cloud Run"
    
    gcloud run deploy "$SERVICE_NAME" \
        --image="$IMAGE_NAME" \
        --platform=managed \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --allow-unauthenticated \
        --set-env-vars="$ENV_VARS" \
        --add-cloudsql-instances="$DB_CONNECTION_NAME" \
        --memory=1Gi \
        --cpu=1 \
        --timeout=300 \
        --max-instances=10 \
        --min-instances=0 \
        --port=8000 \
        --concurrency=80 \
        --quiet
    
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
        --platform=managed \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --format="value(status.url)")
    
    log_success "Service deployed: $SERVICE_URL"
}

run_migrations() {
    log_step "Running Database Migrations"
    
    local job_name="run-migrations-$(date +%s)"
    
    # Create migration job
    gcloud run jobs create "$job_name" \
        --image="$IMAGE_NAME" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --set-env-vars="$ENV_VARS" \
        --add-cloudsql-instances="$DB_CONNECTION_NAME" \
        --command="python" \
        --args="manage.py,migrate,--noinput" \
        --max-retries=3 \
        --memory=512Mi \
        --cpu=1 \
        --timeout=600 \
        --quiet 2>/dev/null || true
    
    # Execute job
    log_info "Executing migrations..."
    if gcloud run jobs execute "$job_name" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --wait; then
        log_success "Migrations completed"
    else
        log_error "Migrations failed"
        exit 1
    fi
}

collect_static_files() {
    log_step "Collecting and Uploading Static Files"
    
    local job_name="collect-static-$(date +%s)"
    
    # Create collectstatic job
    gcloud run jobs create "$job_name" \
        --image="$IMAGE_NAME" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --set-env-vars="$ENV_VARS" \
        --command="python" \
        --args="manage.py,collectstatic,--noinput" \
        --max-retries=3 \
        --memory=512Mi \
        --cpu=1 \
        --timeout=600 \
        --quiet 2>/dev/null || true
    
    # Execute job
    log_info "Collecting static files..."
    if gcloud run jobs execute "$job_name" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --wait; then
        log_success "Static files collected"
        
        # Upload to Cloud Storage
        log_info "Uploading static files to Cloud Storage..."
        # This would be handled by django-storages or a separate upload script
        log_warning "Configure django-storages for automatic static file upload"
    else
        log_warning "Static collection job failed (may be OK if using storage backend)"
    fi
}

seed_database() {
    if [ "$SKIP_SEED" = true ]; then
        log_warning "Skipping database seeding"
        return
    fi
    
    log_step "Seeding Database"
    
    if [ "$AUTO_APPROVE" = false ]; then
        read -p "Do you want to seed the database with sample data? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_warning "Skipping database seeding"
            return
        fi
    fi
    
    local job_name="seed-db-$(date +%s)"
    
    log_info "Creating seed job..."
    gcloud run jobs create "$job_name" \
        --image="$IMAGE_NAME" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --set-env-vars="$ENV_VARS" \
        --add-cloudsql-instances="$DB_CONNECTION_NAME" \
        --command="bash" \
        --args="-c,python,manage.py,seed_realistic,--categories,30,--products,1000" \
        --max-retries=1 \
        --memory=1Gi \
        --cpu=1 \
        --timeout=1800 \
        --quiet 2>/dev/null || true
    
    log_info "Executing seed job (this may take several minutes)..."
    if gcloud run jobs execute "$job_name" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --wait; then
        log_success "Database seeded successfully"
    else
        log_warning "Database seeding failed or was skipped"
    fi
}

print_summary() {
    echo ""
    echo -e "${GREEN}${BOLD}========================================${NC}"
    echo -e "${GREEN}${BOLD}  Deployment Complete! 🎉${NC}"
    echo -e "${GREEN}${BOLD}========================================${NC}"
    echo ""
    echo -e "${CYAN}Deployment Summary:${NC}"
    echo -e "  Project ID: ${BOLD}${PROJECT_ID}${NC}"
    echo -e "  Service URL: ${BOLD}${SERVICE_URL}${NC}"
    echo -e "  Region: ${BOLD}${REGION}${NC}"
    echo -e "  Database: ${BOLD}${DB_INSTANCE_NAME}${NC}"
    echo -e "  Static Bucket: ${BOLD}gs://${BUCKET_NAME_STATIC}${NC}"
    echo -e "  Media Bucket: ${BOLD}gs://${BUCKET_NAME_MEDIA}${NC}"
    echo ""
    echo -e "${YELLOW}${BOLD}Important Credentials (SAVE THESE!):${NC}"
    echo -e "  Database Password: ${BOLD}${DB_PASSWORD}${NC}"
    echo -e "  Secret Key: ${BOLD}${SECRET_KEY}${NC}"
    echo ""
    echo -e "${YELLOW}${BOLD}Next Steps:${NC}"
    echo -e "  1. Configure django-storages in settings.py for Cloud Storage"
    echo -e "  2. Update ALLOWED_HOSTS with your domain"
    echo -e "  3. Set up custom domain mapping in Cloud Run"
    echo -e "  4. Configure Cloud Load Balancer if needed"
    echo -e "  5. Set up monitoring and alerts"
    echo ""
    echo -e "${GREEN}Your application is live at: ${BOLD}${SERVICE_URL}${NC}"
    echo ""
}

# Main execution
main() {
    echo -e "${BLUE}${BOLD}========================================${NC}"
    echo -e "${BLUE}${BOLD}  Django E-commerce GCP Deployment${NC}"
    echo -e "${BLUE}${BOLD}========================================${NC}"
    echo ""
    
    check_requirements
    validate_project
    
    setup_gcp_project
    enable_apis
    setup_database
    setup_storage
    setup_artifact_registry
    build_and_push_image
    get_environment_vars
    deploy_cloud_run
    run_migrations
    collect_static_files
    seed_database
    print_summary
}

# Run main function
main
