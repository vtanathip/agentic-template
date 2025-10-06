@echo off
REM Start RAG Template services with Docker Compose
REM This script starts only the RAG-related services
REM NOTE: Requires Ollama to be installed and running locally on port 11434

echo Starting RAG Template services...

REM Check if local Ollama is running
curl -s http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo WARNING: Ollama is not running on localhost:11434
    echo Please start Ollama locally first:
    echo   - Download from: https://ollama.ai/download/windows
    echo   - Run Ollama Desktop app or: ollama serve
    echo   - Install a model: ollama pull llama3.2
    echo.
)

REM Start core RAG services (without Ollama - using local) + WebUIs
docker-compose -f docker-compose.yml up -d rag-api milvus-standalone etcd minio attu openwebui

echo RAG services are starting up...
echo.
echo Services:
echo - RAG API: http://localhost:8001
echo - Milvus Web UI (Attu): http://localhost:9092
echo - OpenWebUI Chat: http://localhost:3000
echo - Milvus: localhost:19530
echo - Local Ollama: http://localhost:11434 (external)
echo.
echo Wait for services to be healthy before making requests.
echo To install Ollama model: ollama pull llama3.2
echo Check status with: docker-compose ps