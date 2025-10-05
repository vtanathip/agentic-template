"""
Embeddings service for generating text embeddings using sentence-transformers.
"""

import os
from typing import List

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None


class EmbeddingService:
    """Service for generating text embeddings."""

    def __init__(self, model_name: str | None = None):
        """Initialize the embedding service.

        Args:
            model_name: Name of the sentence-transformer model to use.
                       Defaults to 'all-MiniLM-L6-v2' from environment or hardcoded.
        """
        if SentenceTransformer is None:
            raise ImportError("sentence-transformers package is required")

        self.model_name = model_name or os.getenv(
            "EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.model = None

    def _ensure_model_loaded(self):
        """Lazy load the embedding model."""
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            List of floats representing the embedding vector.
        """
        self._ensure_model_loaded()
        if self.model is None:
            raise RuntimeError("Model failed to load")

        embedding = self.model.encode(text, convert_to_tensor=False)
        if hasattr(embedding, 'tolist'):
            return embedding.tolist()
        return list(embedding)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of embedding vectors.
        """
        self._ensure_model_loaded()
        if self.model is None:
            raise RuntimeError("Model failed to load")

        embeddings = self.model.encode(texts, convert_to_tensor=False)
        if hasattr(embeddings, 'tolist'):
            return embeddings.tolist()
        return list(embeddings)

    @property
    def dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        self._ensure_model_loaded()
        if self.model is None:
            raise RuntimeError("Model failed to load")

        # Get dimension by encoding a test string
        test_embedding = self.model.encode("test")
        return len(test_embedding)
