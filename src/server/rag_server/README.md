# RAG Server

A minimal FastAPI server that provides REST API endpoints for the RAG (Retrieval-Augmented Generation) agent.

## Features

- **Document Upload**: Upload documents for indexing via `/upload` endpoint
- **Document Query**: Query the knowledge base via `/query` endpoint
- **Statistics**: Get knowledge base stats via `/stats` endpoint
- **Document Management**: Delete documents via `/documents/{filename}` endpoint
- **Health Check**: Monitor server status via `/health` endpoint

## API Endpoints

### Health Check
- `GET /` - Basic status check
- `GET /health` - Detailed health information

### Document Operations
- `POST /upload` - Upload a document for indexing
- `POST /query` - Query the knowledge base
- `GET /stats` - Get knowledge base statistics
- `DELETE /documents/{filename}` - Delete a specific document

## Usage

### Starting the Server

```bash
# Using the main script
uv run python src/server/rag_server/main.py

# Or directly with uvicorn
uv run uvicorn server.rag_server.app:app --host 0.0.0.0 --port 8001 --reload
```

### Example API Usage

```python
import requests
import json

# Upload a document
with open("document.txt", "rb") as f:
    response = requests.post("http://localhost:8001/upload", files={"file": f})
    print(response.json())

# Query the knowledge base
query_data = {"query": "What is the main topic?"}
response = requests.post("http://localhost:8001/query", json=query_data)
print(response.json())

# Get statistics
response = requests.get("http://localhost:8001/stats")
print(response.json())
```

## Testing

Run the unit tests:

```bash
uv run pytest tests/test_rag_server.py -v
```

## Dependencies

The server requires:
- FastAPI for the web framework
- uvicorn for the ASGI server
- python-multipart for file uploads
- All RAG template dependencies (langgraph, langchain, etc.)

All dependencies are managed via uv and defined in `pyproject.toml`.