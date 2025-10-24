@echo off
REM Unified startup script for Agentic Template

echo Starting Agentic Template with OpenWebUI and Pipelines...
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker Desktop first.
    exit /b 1
)

REM Start all services
echo Starting services...
docker-compose up -d

echo.
echo Waiting for services to be healthy...
timeout /t 10 /nobreak >nul

REM Check service health
echo.
echo Service Status:
docker-compose ps

echo.
echo ================================================================
echo Services are starting up! Access them at:
echo ================================================================
echo.
echo ^🌐 OpenWebUI:          http://localhost:3000
echo ^🔧 Pipelines Server:   http://localhost:9099
echo ^🤖 Agentic API:        http://localhost:8000
echo ^📚 RAG API:            http://localhost:8001
echo ^🗄️  Milvus (Vector DB): http://localhost:19530
echo ^🖥️  Attu (Milvus UI):  http://localhost:9092
echo.
echo ================================================================
echo.
echo Next steps:
echo 1. Wait 30-60 seconds for all services to be healthy
echo 2. Open http://localhost:3000 in your browser
echo 3. The LangGraph RAG pipeline should be automatically available
echo.
echo To view logs: docker-compose logs -f [service-name]
echo To stop: docker-compose down
echo ================================================================
