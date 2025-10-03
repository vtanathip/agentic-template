@echo off
REM Docker Compose startup script for Agentic Template with OpenWebUI (Windows)

echo 🚀 Starting Agentic Template Services (Main + Multi-Agent)...
echo ==================================

REM Change to docker directory
cd /d "%~dp0"

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker and try again.
    pause
    exit /b 1
)

REM Build and start services
echo 📦 Building and starting services...
docker-compose up --build -d

REM Wait a moment for services to initialize
echo ⏳ Waiting for services to initialize...
timeout /t 10 /nobreak >nul

REM Check service status
echo 🔍 Checking service status...
docker-compose ps

echo.
echo ✅ Services started successfully!
echo.
echo 🌐 Access points:
echo   Main Agentic Template:
echo   • API Server: http://localhost:8000
echo   • API Documentation: http://localhost:8000/docs
echo   • Chat Interface: http://localhost:3000
echo.
echo   Multi-Agent Trading System:
echo   • API Server: http://localhost:8001
echo   • API Documentation: http://localhost:8001/docs
echo   • Chat Interface: http://localhost:3001
echo.
echo 📝 To stop services:
echo   docker-compose down
echo.
echo 📊 To view logs:
echo   docker-compose logs -f

pause