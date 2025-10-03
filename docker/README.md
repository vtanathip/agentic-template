# Docker Setup for Agentic Template with OpenWebUI

This directory contains Docker configuration files to run both the main Agentic Template and Multi-Agent Trading System servers with separate OpenWebUI interfaces.

## Files Overview

- `Dockerfile.agentic` - Container configuration for the main agentic FastAPI application
- `Dockerfile.multiagent` - Container configuration for the multi-agent trading system
- `Dockerfile` - Legacy container configuration (kept for backward compatibility)
- `docker-compose.yml` - Orchestrates all services (both APIs and OpenWebUI instances)
- `start-services.bat` - Windows startup script
- `start-services.sh` - Linux/Mac startup script
- `.dockerignore` - Excludes unnecessary files from Docker build context

## Quick Start

### Windows
```bash
cd docker
./start-services.bat
```

### Linux/Mac
```bash
cd docker
chmod +x start-services.sh
./start-services.sh
```

### Manual Start
```bash
cd docker
docker-compose up --build -d
```

## Access Points

Once services are running:

### Main Agentic Template
- **API Server**: <http://localhost:8000>
- **API Documentation**: <http://localhost:8000/docs>
- **Chat Interface**: <http://localhost:3000>

### Multi-Agent Trading System
- **API Server**: <http://localhost:8001>
- **API Documentation**: <http://localhost:8001/docs>
- **Chat Interface**: <http://localhost:3001>

## Service Configuration

### Main Agentic API Service (`agentic-api`)
- **Container**: `agentic-template-api`
- **Port**: 8000
- **Dockerfile**: `Dockerfile.agentic`
- **Health Check**: `/health` endpoint
- **OpenAI-compatible endpoints**: `/v1/models`, `/v1/chat/completions`

### Multi-Agent API Service (`multiagent-api`)
- **Container**: `agentic-multiagent-api`
- **Port**: 8001
- **Dockerfile**: `Dockerfile.multiagent`
- **Health Check**: `/health` endpoint
- **Streaming Support**: Real-time analysis updates

### Main OpenWebUI (`openwebui`)
- **Container**: `agentic-openwebui`
- **Port**: 3000 (mapped from internal 8080)
- **Authentication**: Disabled for development
- **API Base URL**: Points to main agentic API (port 8000)

### Multi-Agent OpenWebUI (`openwebui-multiagent`)
- **Container**: `agentic-multiagent-openwebui`
- **Port**: 3001 (mapped from internal 8080)
- **Authentication**: Disabled for development
- **API Base URL**: Points to multi-agent API (port 8001)

## Development Features

- **Hot Reload**: Source code is mounted for development
- **Health Checks**: Automatic service monitoring
- **Networking**: Internal Docker network for service communication

## Stopping Services

```bash
cd docker
docker-compose down
```

## Viewing Logs

```bash
cd docker
docker-compose logs -f
```

## Troubleshooting

### Services Won't Start
1. Ensure Docker is running
2. Check port availability (8000, 3000)
3. View logs: `docker-compose logs`

### OpenWebUI Can't Connect
1. Verify FastAPI service is healthy: `docker-compose ps`
2. Check FastAPI logs: `docker-compose logs agentic-api`
3. Ensure OpenAI-compatible endpoints are working: `curl http://localhost:8000/v1/models`

### Build Issues
1. Clean Docker cache: `docker system prune`
2. Rebuild without cache: `docker-compose build --no-cache`

## Environment Variables

You can customize the setup by creating a `.env` file in the docker directory:

```env
# FastAPI Configuration
FASTAPI_PORT=8000
UVICORN_HOST=0.0.0.0

# OpenWebUI Configuration
OPENWEBUI_PORT=3000
WEBUI_AUTH=False
WEBUI_NAME=Agentic Template Chat
```