#!/bin/bash

echo "🐳 Starting Django Blog with Docker..."
echo ""

# Stop and remove any existing containers
echo "🧹 Cleaning up old containers..."
docker-compose down

# Build the Docker image
echo "🔨 Building Docker image..."
docker-compose build

# Start the containers
echo "🚀 Starting containers..."
docker-compose up -d

# Wait for container to be ready
echo "⏳ Waiting for Django to be ready..."
sleep 5

# Run migrations
echo "📦 Running migrations..."
docker-compose exec -T web python manage.py migrate

# Create superuser (skip if already exists)
echo "👤 Creating admin user..."
docker-compose exec -T web python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Admin user created!')
else:
    print('ℹ️  Admin user already exists')
EOF

echo ""
echo "✅ Django Blog is running!"
echo ""
echo "📝 Access the application:"
echo "   🌐 Blog: http://localhost:8000"
echo "   ⚙️  Admin: http://localhost:8000/admin"
echo ""
echo "👤 Admin credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📋 To view logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 To stop the application:"
echo "   docker-compose down"

