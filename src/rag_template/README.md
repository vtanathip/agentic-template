# RAG Template

A simple Retrieval-Augmented Generation (RAG) implementation using LangGraph, Docling, Ollama, and Milvus vector database.

## Features

- **File Upload**: Upload and process documents (PDF, Word, TXT) using Docling for extraction
- **Document Retrieval**: Query and retrieve relevant information from indexed documents
- **Vector Storage**: Uses Milvus as the vector database for efficient similarity search
- **LLM Integration**: Leverages Ollama for local language model inference
- **Agent Framework**: Built with LangGraph for robust workflow management

## Architecture

The RAG system consists of:

1. **Document Processor**: Handles file uploads using Docling for high-quality text extraction
2. **Embedding Service**: Generates vector embeddings for text chunks
3. **Vector Store**: Milvus database for storing and retrieving embeddings
4. **Retrieval System**: Searches for relevant document chunks
5. **LangGraph Agent**: Orchestrates the RAG workflow with two main nodes:
   - Upload node: Processes and indexes documents
   - Query node: Retrieves and synthesizes information

## Key Technologies

- **Docling**: Advanced document processing and text extraction
- **LangGraph**: Agent workflow orchestration
- **Milvus**: Vector database for similarity search
- **Ollama**: Local LLM inference
- **Sentence Transformers**: Text embedding generation

## Components

### Core Files

- `agent.py` - Main LangGraph RAG agent implementation
- `document_processor.py` - Docling-based document processing
- `vector_store.py` - Milvus vector database integration
- `retriever.py` - Document retrieval and search functionality
- `embeddings.py` - Text embedding generation

## Usage

### 1. Start Services

```bash
# Start Milvus and other required services
cd docker
docker-compose up -d
```

### 2. Upload Documents

```python
from rag_template.agent import RAGAgent

agent = RAGAgent()
result = agent.upload_document("path/to/document.pdf")
```

### 3. Query Information

```python
response = agent.query("What is the main topic of the uploaded document?")
print(response)
```

## Requirements

- Python 3.12+
- Docker and Docker Compose
- Ollama (for local LLM)
- Milvus (vector database)

## Dependencies

Key dependencies managed via UV:

- `langgraph` - Agent framework
- `langchain` - LLM abstractions
- `docling` - Advanced document processing
- `pymilvus` - Milvus client
- `sentence-transformers` - Text embeddings
- `ollama` - Local LLM client

## Testing

The implementation includes:

- Unit tests for individual components
- Integration tests for the complete RAG pipeline
- Test fixtures for document processing

Run tests with:

```bash
uv run pytest tests/
```

## Environment Variables

```bash
OLLAMA_BASE_URL=http://localhost:11434
MILVUS_HOST=localhost
MILVUS_PORT=19530
EMBEDDING_MODEL=all-MiniLM-L6-v2
```