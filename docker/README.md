# Docker Setup for Agentic Template with OpenWebUI

This directory contains Docker configuration files to run the Agentic Template FastAPI server with OpenWebUI for an interactive chat interface.

## Files Overview

- `Dockerfile` - Container configuration for the FastAPI application
- `docker-compose.yml` - Orchestrates both FastAPI and OpenWebUI services
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

- **FastAPI Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **OpenWebUI Chat Interface**: http://localhost:3000

## Service Configuration

### FastAPI Service (`agentic-api`)
- **Port**: 8000
- **Health Check**: `/health` endpoint
- **OpenAI-compatible endpoints**: `/v1/models`, `/v1/chat/completions`

### OpenWebUI Service (`openwebui`)
- **Port**: 3000 (mapped from internal 8080)
- **Authentication**: Disabled for development
- **API Base URL**: Points to FastAPI service internally

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