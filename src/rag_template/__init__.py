"""
RAG Template - Simple RAG implementation with LangGraph, Docling, and Ollama
"""

__version__ = "0.1.0"

try:
    from .rag_agent import RAGAgent
    from .retriever import DocumentRetriever
    from .document_processor import DoclingProcessor
    from .embeddings import EmbeddingService
    from .vector_store import MilvusVectorStore

    __all__ = [
        "RAGAgent",
        "DocumentRetriever",
        "DoclingProcessor",
        "EmbeddingService",
        "MilvusVectorStore"
    ]
except ImportError:
    # Handle case where dependencies are not installed
    __all__ = []
