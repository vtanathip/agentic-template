"""
Vector store implementation using Milvus for storing and retrieving document embeddings.
"""

import os
from typing import List, Dict, Any, Optional, TYPE_CHECKING

try:
    from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility
    if TYPE_CHECKING:
        # Import for type checking only - helps mypy understand the types
        from pymilvus import Collection as CollectionType
except ImportError:
    connections = None
    Collection = None
    CollectionSchema = None
    FieldSchema = None
    DataType = None
    utility = None
    if TYPE_CHECKING:
        CollectionType = None  # type: ignore


class MilvusVectorStore:
    """Milvus vector database interface for RAG."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        collection_name: str = "rag_documents",
        dimension: int = 384
    ):
        """Initialize Milvus vector store.

        Args:
            host: Milvus server host. Defaults to localhost or MILVUS_HOST env var.
            port: Milvus server port. Defaults to 19530 or MILVUS_PORT env var.
            collection_name: Name of the collection to store documents.
            dimension: Dimension of embedding vectors.
        """
        if connections is None:
            raise ImportError("pymilvus package is required")

        self.host = host or os.getenv("MILVUS_HOST", "localhost")
        self.port = int(port or os.getenv("MILVUS_PORT", "19530"))
        self.collection_name = collection_name
        self.dimension = dimension
        self.collection: Optional["Collection"] = None  # Type hint for better IDE support

    def connect(self):
        """Connect to Milvus server."""
        if connections is None or Collection is None or utility is None:
            raise ImportError("pymilvus package is required")

        connections.connect(
            alias="default",
            host=self.host,
            port=self.port
        )

        # Create collection if it doesn't exist
        if not utility.has_collection(self.collection_name):
            self._create_collection()

        self.collection = Collection(self.collection_name)

        # Load collection for searching
        self.collection.load()

    def _create_collection(self):
        """Create a new collection with the required schema."""
        if FieldSchema is None or DataType is None or CollectionSchema is None or Collection is None:
            raise ImportError("pymilvus package is required")

        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR,
                        max_length=512, is_primary=True),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="chunk_index", dtype=DataType.INT64),
            FieldSchema(name="embedding",
                        dtype=DataType.FLOAT_VECTOR, dim=self.dimension)
        ]

        schema = CollectionSchema(
            fields=fields,
            description="RAG document chunks with embeddings"
        )

        collection = Collection(name=self.collection_name, schema=schema)

        # Create index for vector field
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        collection.create_index(field_name="embedding",
                                index_params=index_params)

    def add_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Add documents with embeddings to the vector store.

        Args:
            documents: List of document chunks with metadata.
            embeddings: Corresponding embedding vectors.
        """
        if not self.collection:
            raise RuntimeError("Must call connect() before adding documents")

        if len(documents) != len(embeddings):
            raise ValueError(
                "Number of documents must match number of embeddings")

        # Prepare data for insertion
        data = [
            [doc["id"] for doc in documents],  # ids
            [doc["text"] for doc in documents],  # text
            [doc["source"] for doc in documents],  # source
            [doc["chunk_index"] for doc in documents],  # chunk_index
            embeddings  # embedding vectors
        ]

        # Insert data
        self.collection.insert(data)

        # Flush to ensure data is written
        self.collection.flush()

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        source_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents.

        Args:
            query_embedding: Query embedding vector.
            top_k: Number of top results to return.
            source_filter: Optional filter by source filename.

        Returns:
            List of similar documents with scores.
        """
        if not self.collection:
            raise RuntimeError("Must call connect() before searching")

        search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}

        # Build expression for filtering
        expr = None
        if source_filter:
            expr = f'source == "{source_filter}"'

        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=expr,
            output_fields=["id", "text", "source", "chunk_index"]
        )

        # Format results
        documents = []
        for result in results[0]:
            documents.append({
                "id": result.entity.get("id"),
                "text": result.entity.get("text"),
                "source": result.entity.get("source"),
                "chunk_index": result.entity.get("chunk_index"),
                "score": result.score,
                "distance": result.distance
            })

        return documents

    def delete_by_source(self, source: str):
        """Delete all documents from a specific source.

        Args:
            source: Source filename to delete.
        """
        if not self.collection:
            raise RuntimeError("Must call connect() before deleting documents")

        expr = f'source == "{source}"'
        self.collection.delete(expr)
        self.collection.flush()

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection.

        Returns:
            Dictionary with collection statistics.
        """
        if not self.collection:
            raise RuntimeError("Must call connect() before getting stats")

        # Use num_entities instead of get_stats() which doesn't exist
        row_count = self.collection.num_entities
        
        return {
            "row_count": row_count,
            "collection_name": self.collection_name,
            "index_type": "IVF_FLAT",
            "metric_type": "L2"
        }

    def disconnect(self):
        """Disconnect from Milvus server."""
        if self.collection:
            self.collection.release()
        if connections:
            connections.disconnect("default")
