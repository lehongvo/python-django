@echo off
echo Starting Django Blog with Docker...

REM Stop and remove any existing containers
echo Cleaning up old containers...
docker-compose down

REM Build the Docker image
echo Building Docker image...
docker-compose build

REM Start the containers
echo Starting containers...
docker-compose up -d

echo.
echo Django Blog is starting...
echo.
echo Access the application:
echo   Blog: http://localhost:8000
echo   Admin: http://localhost:8000/admin
echo.
echo Admin credentials:
echo   Username: admin
echo   Password: admin123
echo.
pause

