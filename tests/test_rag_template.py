"""
Unit tests for RAG template components.
"""

import pytest
import tempfile
import io
from unittest.mock import Mock, patch, MagicMock

# Import the modules we want to test
from rag_template.document_processor import DoclingProcessor
from rag_template.embeddings import EmbeddingService
from rag_template.vector_store import MilvusVectorStore
from rag_template.retriever import DocumentRetriever


class TestDoclingProcessor:
    """Test cases for DoclingProcessor."""

    def setup_method(self):
        """Setup for each test method."""
        self.processor = DoclingProcessor(chunk_size=100, chunk_overlap=20)

    @patch('rag_template.document_processor.DocumentConverter')
    def test_process_text_file(self, mock_converter_class):
        """Test processing a text file."""
        # Mock the converter
        mock_converter = MagicMock()
        mock_converter_class.return_value = mock_converter

        # Mock the conversion result
        mock_result = MagicMock()
        mock_result.document.export_to_markdown.return_value = "This is test content for processing."
        mock_result.document.pages = []
        mock_result.document.title = "Test Document"
        mock_converter.convert.return_value = mock_result

        # Test file content
        file_content = io.BytesIO(b"This is test content for processing.")

        # Process the file
        documents = self.processor.process_file(file_content, "test.txt")

        # Assertions
        assert len(documents) > 0
        assert documents[0]["source"] == "test.txt"
        assert documents[0]["chunk_index"] == 0
        assert "This is test content" in documents[0]["text"]

    def test_split_text(self):
        """Test text splitting functionality."""
        text = "This is a long text. " * 10  # Create text longer than chunk_size

        chunks = self.processor._split_text(text)

        assert len(chunks) > 1
        assert all(len(chunk) <= self.processor.chunk_size +
                   50 for chunk in chunks)  # Allow some flexibility

    def test_get_supported_formats(self):
        """Test getting supported file formats."""
        formats = self.processor.get_supported_formats()

        assert '.pdf' in formats
        assert '.docx' in formats
        assert '.txt' in formats

    def test_unsupported_file_type(self):
        """Test handling of unsupported file types."""
        file_content = io.BytesIO(b"test content")

        with pytest.raises(ValueError, match="Unsupported file type"):
            self.processor.process_file(file_content, "test.unsupported")


class TestEmbeddingService:
    """Test cases for EmbeddingService."""

    @patch('rag_template.embeddings.SentenceTransformer')
    def test_embed_text(self, mock_transformer_class):
        """Test single text embedding."""
        # Mock the transformer
        mock_transformer = MagicMock()
        mock_transformer_class.return_value = mock_transformer
        mock_transformer.encode.return_value = [0.1, 0.2, 0.3]

        service = EmbeddingService("test-model")

        embedding = service.embed_text("test text")

        assert embedding == [0.1, 0.2, 0.3]
        mock_transformer.encode.assert_called_once_with(
            "test text", convert_to_tensor=False)

    @patch('rag_template.embeddings.SentenceTransformer')
    def test_embed_texts(self, mock_transformer_class):
        """Test multiple text embeddings."""
        # Mock the transformer
        mock_transformer = MagicMock()
        mock_transformer_class.return_value = mock_transformer
        mock_transformer.encode.return_value = [[0.1, 0.2], [0.3, 0.4]]

        service = EmbeddingService("test-model")

        embeddings = service.embed_texts(["text1", "text2"])

        assert embeddings == [[0.1, 0.2], [0.3, 0.4]]
        mock_transformer.encode.assert_called_once_with(
            ["text1", "text2"], convert_to_tensor=False)

    @patch('rag_template.embeddings.SentenceTransformer')
    def test_dimension_property(self, mock_transformer_class):
        """Test getting embedding dimension."""
        # Mock the transformer
        mock_transformer = MagicMock()
        mock_transformer_class.return_value = mock_transformer
        mock_transformer.encode.return_value = [0.1, 0.2, 0.3]

        service = EmbeddingService("test-model")

        dimension = service.dimension

        assert dimension == 3


class TestMilvusVectorStore:
    """Test cases for MilvusVectorStore."""

    @patch('rag_template.vector_store.connections')
    @patch('rag_template.vector_store.utility')
    @patch('rag_template.vector_store.Collection')
    def test_connect(self, mock_collection_class, mock_utility, mock_connections):
        """Test connecting to Milvus."""
        # Mock utility
        mock_utility.has_collection.return_value = True

        # Mock collection
        mock_collection = MagicMock()
        mock_collection_class.return_value = mock_collection

        store = MilvusVectorStore(host="test-host", port=19530)
        store.connect()

        mock_connections.connect.assert_called_once_with(
            alias="default",
            host="test-host",
            port=19530
        )
        mock_collection.load.assert_called_once()

    @patch('rag_template.vector_store.connections')
    @patch('rag_template.vector_store.utility')
    @patch('rag_template.vector_store.Collection')
    def test_add_documents(self, mock_collection_class, mock_utility, mock_connections):
        """Test adding documents to vector store."""
        # Mock setup
        mock_utility.has_collection.return_value = True
        mock_collection = MagicMock()
        mock_collection_class.return_value = mock_collection

        store = MilvusVectorStore()
        store.connect()

        # Test data
        documents = [
            {"id": "doc1", "text": "test1", "source": "file1", "chunk_index": 0},
            {"id": "doc2", "text": "test2", "source": "file1", "chunk_index": 1}
        ]
        embeddings = [[0.1, 0.2], [0.3, 0.4]]

        store.add_documents(documents, embeddings)

        mock_collection.insert.assert_called_once()
        mock_collection.flush.assert_called_once()


class TestDocumentRetriever:
    """Test cases for DocumentRetriever."""

    @patch('rag_template.retriever.DoclingProcessor')
    @patch('rag_template.retriever.EmbeddingService')
    @patch('rag_template.retriever.MilvusVectorStore')
    def test_upload_document(self, mock_vector_store_class, mock_embedding_service_class, mock_processor_class):
        """Test document upload functionality."""
        # Mock components
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor

        mock_embedding_service = MagicMock()
        mock_embedding_service_class.return_value = mock_embedding_service
        mock_embedding_service.dimension = 384

        mock_vector_store = MagicMock()
        mock_vector_store_class.return_value = mock_vector_store

        # Mock processing results
        mock_documents = [
            {"id": "doc1", "text": "test content", "source": "test.txt", "chunk_index": 0}]
        mock_processor.process_file.return_value = mock_documents

        mock_embeddings = [[0.1, 0.2, 0.3]]
        mock_embedding_service.embed_texts.return_value = mock_embeddings

        retriever = DocumentRetriever()

        file_content = io.BytesIO(b"test content")
        result = retriever.upload_document(file_content, "test.txt")

        assert result["success"] is True
        assert "test.txt" in result["message"]
        assert result["chunks_processed"] == 1

    @patch('rag_template.retriever.DoclingProcessor')
    @patch('rag_template.retriever.EmbeddingService')
    @patch('rag_template.retriever.MilvusVectorStore')
    def test_search_documents(self, mock_vector_store_class, mock_embedding_service_class, mock_processor_class):
        """Test document search functionality."""
        # Mock components
        mock_embedding_service = MagicMock()
        mock_embedding_service_class.return_value = mock_embedding_service
        mock_embedding_service.dimension = 384

        mock_vector_store = MagicMock()
        mock_vector_store_class.return_value = mock_vector_store

        # Mock search results
        mock_results = [
            {"id": "doc1", "text": "relevant content", "score": 0.95}]
        mock_vector_store.search.return_value = mock_results

        mock_query_embedding = [0.1, 0.2, 0.3]
        mock_embedding_service.embed_text.return_value = mock_query_embedding

        retriever = DocumentRetriever()

        results = retriever.search_documents("test query")

        assert len(results) == 1
        assert results[0]["text"] == "relevant content"
        assert results[0]["score"] == 0.95
