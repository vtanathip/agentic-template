"""
Retrieval system that combines document processing, embeddings, and vector search.
"""

from typing import List, Dict, Any, BinaryIO, Optional
from .document_processor import DoclingProcessor
from .embeddings import EmbeddingService
from .vector_store import MilvusVectorStore


class DocumentRetriever:
    """Handles document upload and retrieval for RAG system."""

    def __init__(
        self,
        milvus_host: str | None = None,
        milvus_port: int | None = None,
        embedding_model: str | None = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """Initialize the document retriever.

        Args:
            milvus_host: Milvus server host.
            milvus_port: Milvus server port.
            embedding_model: Name of the embedding model to use.
            chunk_size: Size of text chunks for processing.
            chunk_overlap: Overlap between consecutive chunks.
        """
        self.document_processor = DoclingProcessor(chunk_size, chunk_overlap)
        self.embedding_service = EmbeddingService(embedding_model)

        # Initialize vector store with proper dimension
        try:
            dimension = self.embedding_service.dimension
        except Exception:
            # Fallback dimension if model can't be loaded yet
            dimension = 384

        self.vector_store = MilvusVectorStore(
            host=milvus_host,
            port=milvus_port,
            dimension=dimension
        )
        self._connected = False

    def connect(self):
        """Connect to the vector database."""
        if not self._connected:
            self.vector_store.connect()
            self._connected = True

    def upload_document(self, file_content: BinaryIO, filename: str) -> Dict[str, Any]:
        """Upload and process a document for retrieval.

        Args:
            file_content: Binary file content.
            filename: Name of the uploaded file.

        Returns:
            Dictionary with upload results and statistics.
        """
        try:
            self.connect()

            # Process the document into chunks
            documents = self.document_processor.process_file(
                file_content, filename)

            if not documents:
                return {
                    "success": False,
                    "message": "No text content found in the document",
                    "chunks_processed": 0
                }

            # Generate embeddings for all chunks
            texts = [doc["text"] for doc in documents]
            embeddings = self.embedding_service.embed_texts(texts)

            # Store in vector database
            self.vector_store.add_documents(documents, embeddings)

            return {
                "success": True,
                "message": f"Successfully processed {filename}",
                "filename": filename,
                "chunks_processed": len(documents),
                "total_characters": sum(len(doc["text"]) for doc in documents)
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error processing document: {str(e)}",
                "chunks_processed": 0
            }

    def search_documents(
        self,
        query: str,
        top_k: int = 5,
        source_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for relevant document chunks.

        Args:
            query: Search query text.
            top_k: Number of top results to return.
            source_filter: Optional filter by source filename.

        Returns:
            List of relevant document chunks with similarity scores.
        """
        try:
            self.connect()

            # Generate embedding for the query
            query_embedding = self.embedding_service.embed_text(query)

            # Search in vector database
            results = self.vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k,
                source_filter=source_filter
            )

            return results

        except Exception as e:
            return [{
                "error": str(e),
                "text": f"Error during search: {str(e)}",
                "score": 0.0
            }]

    def delete_document(self, filename: str) -> Dict[str, Any]:
        """Delete all chunks from a specific document.

        Args:
            filename: Name of the document to delete.

        Returns:
            Dictionary with deletion results.
        """
        try:
            self.connect()
            self.vector_store.delete_by_source(filename)
            return {
                "success": True,
                "message": f"Successfully deleted document: {filename}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error deleting document: {str(e)}"
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the document collection.

        Returns:
            Dictionary with collection statistics.
        """
        try:
            self.connect()
            return self.vector_store.get_collection_stats()
        except Exception as e:
            return {
                "error": str(e),
                "row_count": 0
            }

    def disconnect(self):
        """Disconnect from the vector database."""
        if self._connected:
            self.vector_store.disconnect()
            self._connected = False
