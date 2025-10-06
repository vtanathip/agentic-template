#!/bin/bash

# Start RAG Template services with Docker Compose
# This script starts only the RAG-related services
# NOTE: Requires Ollama to be installed and running locally on port 11434

echo "Starting RAG Template services..."

# Check if local Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "WARNING: Ollama is not running on localhost:11434"
    echo "Please start Ollama locally first:"
    echo "  - Install: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "  - Run: ollama serve"
    echo "  - Install a model: ollama pull llama3.2"
    echo ""
fi

# Start core RAG services (without Ollama - using local) + WebUIs
docker-compose -f docker-compose.yml up -d \
  rag-api \
  milvus-standalone \
  etcd \
  minio \
  attu \
  openwebui

echo "RAG services are starting up..."
echo ""
echo "Services:"
echo "- RAG API: http://localhost:8001"
echo "- Milvus Web UI (Attu): http://localhost:9092"
echo "- OpenWebUI Chat: http://localhost:3000"
echo "- Milvus: localhost:19530"
echo "- Local Ollama: http://localhost:11434 (external)"
echo ""
echo "Wait for services to be healthy before making requests."
echo "To install Ollama model: ollama pull llama3.2"
echo "Check status with: docker-compose ps"