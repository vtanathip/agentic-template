# RAG Template Docker Setup

This directory contains Docker configuration for running the RAG (Retrieval-Augmented Generation) template with minimal dependencies.

## Files

- `Dockerfile.rag` - Minimal Docker image for RAG template using uv package manager
- `pyproject.rag.toml` - Minimal dependencies for RAG functionality
- `start-rag-services.sh` / `start-rag-services.bat` - Scripts to start RAG services
- `docker-compose.yml` - Updated to include RAG services and dependencies

## Services Added

### Core RAG Service
- **rag-api**: RAG template API server (port 8001)

### Dependencies
- **milvus-standalone**: Vector database for embeddings (port 19530)
- **etcd**: Metadata store for Milvus
- **minio**: Object storage for Milvus

### External Dependencies (Local Installation Required)
- **Ollama**: Local LLM server (port 11434) - Must be installed and running locally

## Prerequisites

### Install Ollama Locally
```bash
# Linux/Mac
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download from: https://ollama.ai/download/windows
```

### Install a Model
```bash
# Install a model (required for LLM responses)
ollama pull llama3.2

# Or use a smaller model for testing
ollama pull llama3.2:1b
```

### Start Ollama Service
```bash
# Start Ollama server
ollama serve
```

## Quick Start

### Start RAG Services Only
```bash
# Linux/Mac
./start-rag-services.sh

# Windows
start-rag-services.bat
```

### Start All Services
```bash
docker-compose up -d
```

## Endpoints

- RAG API: http://localhost:8001
- RAG API Health: http://localhost:8001/health
- RAG API Docs: http://localhost:8001/docs
- Ollama API: http://localhost:11434
- Milvus: localhost:19530

## Usage

1. Start the services
2. Wait for health checks to pass
3. Upload documents via `/upload` endpoint
4. Query documents via `/query` endpoint

## Environment Variables

The RAG service is configured with:
- `MILVUS_HOST=milvus-standalone`
- `MILVUS_PORT=19530`
- `OLLAMA_BASE_URL=http://host.docker.internal:11434` (connects to local Ollama)

## Volume Mounts

For development, the source code is mounted read-only:
- `../src/rag_template:/app/src/rag_template:ro`
- `../src/server/rag_server:/app/src/server/rag_server:ro`

## Data Persistence

The following volumes store persistent data:
- `milvus-data`: Vector database data
- `ollama-data`: Downloaded models
- `etcd-data`: Milvus metadata
- `minio-data`: Object storage data