#!/bin/bash

# Docker Compose startup script for Agentic Template with OpenWebUI

echo "🚀 Starting Agentic Template Services (Main + Multi-Agent)..."
echo "=================================="

# Change to docker directory
cd "$(dirname "$0")/docker"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build and start services
echo "📦 Building and starting services..."
docker-compose up --build -d

# Wait a moment for services to initialize
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check service status
echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "✅ Services started successfully!"
echo ""
echo "🌐 Access points:"
echo "  Main Agentic Template:"
echo "  • API Server: http://localhost:8000"
echo "  • API Documentation: http://localhost:8000/docs"
echo "  • Chat Interface: http://localhost:3000"
echo ""
echo "  Multi-Agent Trading System:"
echo "  • API Server: http://localhost:8001"
echo "  • API Documentation: http://localhost:8001/docs"
echo "  • Chat Interface: http://localhost:3001"
echo ""
echo "📝 To stop services:"
echo "  docker-compose -f docker/docker-compose.yml down"
echo ""
echo "📊 To view logs:"
echo "  docker-compose -f docker/docker-compose.yml logs -f"