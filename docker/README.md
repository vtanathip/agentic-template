# Docker Setup for Agentic Template# Docker Setup for Agentic Template with OpenWebUI



This directory contains Docker configuration files to run the complete Agentic Template system with RAG (Retrieval-Augmented Generation), OpenWebUI, and pipeline support.This directory contains Docker configuration files to run the Agentic Template FastAPI server with OpenWebUI for an interactive chat interface.



## 🏗️ Architecture## Files Overview



The system consists of 8 Docker services:- `Dockerfile` - Container configuration for the FastAPI application

- `docker-compose.yml` - Orchestrates both FastAPI and OpenWebUI services

### Core API Services- `start-services.bat` - Windows startup script

- **agentic-api** (port 8000): Original agentic FastAPI server- `start-services.sh` - Linux/Mac startup script

- **rag-api** (port 8001): RAG template API server with streaming support- `.dockerignore` - Excludes unnecessary files from Docker build context



### User Interface## Quick Start

- **openwebui** (port 3000): Web-based chat interface with pipeline integration

- **pipelines** (port 9099): OpenWebUI pipelines server for custom integrations### Windows

```bash

### Vector Database Stack (Milvus)cd docker

- **milvus-standalone** (port 19530): Vector database for embeddings./start-services.bat

- **attu** (port 9092): Web UI for Milvus management```

- **etcd**: Metadata store for Milvus

- **minio**: Object storage for Milvus### Linux/Mac

```bash

### External Dependencies (Local Installation Required)cd docker

- **Ollama** (port 11434): Local LLM server - Must be installed and running locallychmod +x start-services.sh

./start-services.sh

## 📋 Prerequisites```



### 1. Install Docker### Manual Start

Ensure Docker Desktop is installed and running.```bash

cd docker

### 2. Install Ollama Locallydocker-compose up --build -d

```bash```

# Linux/Mac

curl -fsSL https://ollama.ai/install.sh | sh## Access Points



# WindowsOnce services are running:

# Download from: https://ollama.ai/download/windows

```- **FastAPI Server**: http://localhost:8000

- **API Documentation**: http://localhost:8000/docs

### 3. Install a Model- **OpenWebUI Chat Interface**: http://localhost:3000

```bash

# Install a model (required for LLM responses)## Service Configuration

ollama pull llama3.2

### FastAPI Service (`agentic-api`)

# Or use a smaller model for testing- **Port**: 8000

ollama pull llama3.2:1b- **Health Check**: `/health` endpoint

```- **OpenAI-compatible endpoints**: `/v1/models`, `/v1/chat/completions`



### 4. Start Ollama Service### OpenWebUI Service (`openwebui`)

```bash- **Port**: 3000 (mapped from internal 8080)

# Start Ollama server (must be running before starting Docker services)- **Authentication**: Disabled for development

ollama serve- **API Base URL**: Points to FastAPI service internally

```

## Development Features

## 🚀 Quick Start

- **Hot Reload**: Source code is mounted for development

### Windows- **Health Checks**: Automatic service monitoring

```bash- **Networking**: Internal Docker network for service communication

cd docker

./start.bat## Stopping Services

```

```bash

### Linux/Maccd docker

```bashdocker-compose down

cd docker```

chmod +x start.sh

./start.sh## Viewing Logs

```

```bash

### Manual Startcd docker

```bashdocker-compose logs -f

cd docker```

docker-compose up -d

```## Troubleshooting



## 🌐 Access Points### Services Won't Start

1. Ensure Docker is running

Once services are running:2. Check port availability (8000, 3000)

3. View logs: `docker-compose logs`

- **OpenWebUI Chat**: http://localhost:3000 (main user interface)

- **Pipelines Server**: http://localhost:9099 (pipeline management)### OpenWebUI Can't Connect

- **Agentic API**: http://localhost:8000 (original API)1. Verify FastAPI service is healthy: `docker-compose ps`

- **RAG API**: http://localhost:8001 (RAG with streaming)2. Check FastAPI logs: `docker-compose logs agentic-api`

- **Milvus Vector DB**: http://localhost:195303. Ensure OpenAI-compatible endpoints are working: `curl http://localhost:8000/v1/models`

- **Attu (Milvus UI)**: http://localhost:9092 (database management)

- **Ollama API**: http://localhost:11434 (local LLM)### Build Issues

1. Clean Docker cache: `docker system prune`

### API Documentation2. Rebuild without cache: `docker-compose build --no-cache`

- **Agentic API Docs**: http://localhost:8000/docs

- **RAG API Docs**: http://localhost:8001/docs## Environment Variables



## 🔧 Service ConfigurationYou can customize the setup by creating a `.env` file in the docker directory:



### RAG API Service (`rag-api`)```env

- **Port**: 8001# FastAPI Configuration

- **Health Check**: `/health` endpointFASTAPI_PORT=8000

- **Features**: Document upload, RAG queries with streaming supportUVICORN_HOST=0.0.0.0

- **Environment**:

  - `MILVUS_HOST=milvus-standalone`# OpenWebUI Configuration

  - `OLLAMA_BASE_URL=http://host.docker.internal:11434`OPENWEBUI_PORT=3000

WEBUI_AUTH=False

### OpenWebUI Service (`openwebui`)WEBUI_NAME=Agentic Template Chat

- **Port**: 3000 (mapped from internal 8080)```
- **Authentication**: Disabled for development (`WEBUI_AUTH=False`)
- **Pipeline Integration**: Configured to use pipelines service
- **API Key**: `0p3n-w3bu!` (for pipeline authentication)

### Pipelines Service (`pipelines`)
- **Port**: 9099
- **Purpose**: Custom pipeline integrations for OpenWebUI
- **Active Pipeline**: LangGraph RAG pipeline with streaming
- **API Key**: `0p3n-w3bu!`
- **Mount**: `../openwebui/pipelines` → `/app/pipelines`

## 📁 Files Overview

- `Dockerfile` - Container for original agentic API
- `Dockerfile.rag` - Container for RAG API (includes OpenGL libraries for PDF processing)
- `docker-compose.yml` - Orchestrates all 8 services
- `start.bat` / `start.sh` - Unified startup scripts
- `pyproject.rag.toml` - Dependencies for RAG functionality
- `test_integration.py` - Integration tests

## 💡 Usage

### Web Interface (Recommended)
1. Start all services using `start.bat` or `start.sh`
2. Wait 30-60 seconds for services to be healthy
3. Open http://localhost:3000 in your browser
4. The LangGraph RAG pipeline should be automatically available
5. Upload documents and ask questions through the chat interface

### API Interface (Programmatic)
1. Upload documents: `POST http://localhost:8001/upload`
2. Query with streaming: `POST http://localhost:8001/query` with `{"query": "...", "stream": true}`
3. View full documentation: http://localhost:8001/docs

### Pipeline Management
The OpenWebUI pipelines server provides custom integration capabilities:
- **Active Pipeline**: LangGraph RAG with streaming
- **Configuration**: Managed through OpenWebUI settings
- **API Key**: `0p3n-w3bu!` (required for authentication)

## 🔑 Key Features

### Complete RAG Experience
- **Web Chat Interface**: User-friendly OpenWebUI
- **REST API**: Programmatic access with streaming support
- **Interactive Docs**: Auto-generated API documentation
- **Local LLM**: Uses local Ollama for privacy and performance
- **Vector Search**: Milvus vector database with web UI
- **PDF Processing**: Supports document upload and processing
- **Streaming Responses**: SSE streaming with OpenAI-compatible format

### Both Interfaces Available
- **OpenWebUI Chat**: Perfect for end-users and testing
- **RAG API**: Ideal for integration and development
- **Shared Backend**: Both use the same RAG services and data

## 🔄 Development Features

- **Hot Reload**: Source code is mounted for development (read-only)
- **Health Checks**: Automatic service monitoring
- **Networking**: Internal Docker network (`agentic-network`) for service communication
- **Volume Persistence**: Data persists across container restarts

## 📦 Volume Mounts

### Source Code (Read-Only for Development)
- `../src/agentic_template:/app/src/agentic_template:ro`
- `../src/rag_template:/app/src/rag_template:ro`
- `../src/server:/app/src/server:ro`
- `../openwebui/pipelines:/app/pipelines`

### Persistent Data
- `openwebui-data`: OpenWebUI settings and data
- `pipelines-data`: Pipeline configurations
- `milvus-data`: Vector database data
- `etcd-data`: Milvus metadata
- `minio-data`: Object storage data

**Note**: Ollama models are stored locally on your host system, not in Docker volumes.

## 🛑 Stopping Services

```bash
cd docker
docker-compose down
```

To also remove volumes:
```bash
docker-compose down -v
```

## 📊 Viewing Logs

```bash
# All services
cd docker
docker-compose logs -f

# Specific service
docker-compose logs -f rag-api
docker-compose logs -f openwebui
docker-compose logs -f pipelines
```

## 🐛 Troubleshooting

### Services Won't Start
1. Ensure Docker Desktop is running
2. Ensure Ollama is running locally: `ollama serve`
3. Check port availability (3000, 8000, 8001, 9099, 11434, 19530, 9092)
4. View service status: `docker-compose ps`
5. View logs: `docker-compose logs`

### OpenWebUI Can't Connect to Pipeline
1. Verify pipelines service is healthy: `docker-compose ps pipelines`
2. Check pipeline logs: `docker-compose logs pipelines`
3. Verify API key is correct: `0p3n-w3bu!`
4. Check OpenWebUI settings: Settings → Admin Settings → Connections

### RAG Queries Fail
1. Verify Ollama is running: `curl http://localhost:11434/api/tags`
2. Check Milvus is healthy: `docker-compose ps milvus-standalone`
3. Check RAG API logs: `docker-compose logs rag-api`
4. Verify documents are uploaded (check via Attu UI at http://localhost:9092)

### PDF Upload Errors
The Dockerfile.rag includes necessary OpenGL libraries for PDF processing:
- libgl1, libglib2.0-0, libsm6, libxext6, libxrender-dev, libgomp1

If issues persist:
1. Check container logs: `docker-compose logs rag-api`
2. Rebuild without cache: `docker-compose build --no-cache rag-api`

### Build Issues
1. Clean Docker cache: `docker system prune`
2. Rebuild without cache: `docker-compose build --no-cache`
3. Check disk space: `docker system df`

### Pipeline Not Loading
1. Check file exists: `../openwebui/pipelines/langgraph_pipeline.py`
2. Verify mount in docker-compose.yml
3. Check pipelines logs for Python errors: `docker-compose logs pipelines`
4. Restart pipelines service: `docker-compose restart pipelines`

## 🔐 Environment Variables

You can customize the setup by creating a `.env` file in the docker directory:

```env
# API Ports
AGENTIC_PORT=8000
RAG_PORT=8001
OPENWEBUI_PORT=3000
PIPELINES_PORT=9099

# Authentication
PIPELINES_API_KEY=0p3n-w3bu!
WEBUI_AUTH=False

# Ollama Configuration
OLLAMA_BASE_URL=http://host.docker.internal:11434

# Milvus Configuration
MILVUS_HOST=milvus-standalone
MILVUS_PORT=19530
```

## 🧪 Testing

Run integration tests:
```bash
cd docker
python test_integration.py
```

The tests verify:
- Service health checks
- Document upload functionality
- RAG query responses
- Streaming support

## 📝 Notes

### Streaming Support
The RAG API supports Server-Sent Events (SSE) streaming:
- Set `stream: true` in query request for streaming
- Returns OpenAI-compatible delta format
- Supports both streaming and non-streaming modes

### Pipeline Architecture
The OpenWebUI pipeline (`langgraph_pipeline.py`) is RAG-focused:
- Removed dual-mode complexity (agentic/RAG)
- Single purpose: RAG queries with streaming
- Direct integration with RAG API server
- Automatic streaming to frontend

### Network Architecture
All services communicate via internal Docker network:
- Services use container names for internal communication
- Host ports exposed for external access
- `host.docker.internal` used to access local Ollama

## 📚 Additional Documentation

- **RAG Template**: `../src/rag_template/README.md`
- **RAG Server**: `../src/server/rag_server/README.md`
- **Streaming Support**: `../src/server/rag_server/STREAMING_SUPPORT.md`

## 🆘 Support

For issues and questions:
1. Check service logs: `docker-compose logs <service-name>`
2. Verify service health: `docker-compose ps`
3. Check API documentation: http://localhost:8001/docs
4. Review integration tests: `test_integration.py`
