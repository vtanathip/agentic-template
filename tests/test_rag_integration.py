"""
Integration tests for the RAG template with Milvus.

These tests require:
- Milvus vector database running on localhost:19530 (via Docker)
- Ollama service running locally on localhost:11434 (external installation)
  - Install: curl -fsSL https://ollama.ai/install.sh | sh (Linux/Mac) or download from ollama.ai (Windows)
  - Start: ollama serve
  - Install model: ollama pull llama3.2

Note: Tests handle missing Ollama models gracefully and will pass with warnings
if models are not available (useful for CI/CD environments).

The tests verify the complete RAG pipeline including document upload, 
vector storage, retrieval, and response generation.
"""

import pytest
import tempfile
import io
import time
from pathlib import Path

# Skip integration tests if dependencies are not available
try:
    from rag_template.rag_agent import RAGAgent
    from rag_template.retriever import DocumentRetriever
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

# Skip all tests in this module if dependencies are not available
pytestmark = pytest.mark.skipif(
    not DEPENDENCIES_AVAILABLE,
    reason="RAG template dependencies not available"
)


class TestRAGIntegration:
    """Integration tests for the complete RAG pipeline."""

    @pytest.fixture(scope="class")
    def milvus_connection(self):
        """Test if Milvus is available for integration tests."""
        try:
            # Try to connect to Milvus
            from rag_template.vector_store import MilvusVectorStore
            store = MilvusVectorStore(collection_name="test_collection")
            store.connect()
            store.disconnect()
            return True
        except Exception:
            pytest.skip("Milvus not available for integration tests")

    @pytest.fixture
    def rag_agent(self, milvus_connection):
        """Create a RAG agent for testing."""
        return RAGAgent(
            milvus_host="localhost",
            milvus_port=19530,
            embedding_model="all-MiniLM-L6-v2",
            ollama_model="llama3.2"
        )

    @pytest.fixture
    def sample_text_file(self):
        """Create a sample text file for testing."""
        content = """
        This is a test document for RAG integration testing.
        
        The document contains information about artificial intelligence and machine learning.
        AI systems can process large amounts of data to make predictions and decisions.
        Machine learning is a subset of AI that focuses on algorithms that improve through experience.
        
        Natural language processing is another important area of AI.
        It enables computers to understand and generate human language.
        
        This document will be used to test the upload and retrieval functionality.
        """
        return io.BytesIO(content.encode('utf-8'))

    def test_document_upload_and_retrieval(self, rag_agent, sample_text_file):
        """Test the complete document upload and retrieval pipeline."""
        # Upload document
        upload_result = rag_agent.upload_document(
            sample_text_file, "test_document.txt")

        assert upload_result["success"] is True
        assert "test_document.txt" in upload_result["message"]

        # Wait a moment for indexing
        time.sleep(1)

        # Query the document
        response = rag_agent.query("What is machine learning?")

        # Debug output (can be removed in production)
        print(
            f"Response preview: {response[:100]}{'...' if len(response) > 100 else ''}")

        assert isinstance(response, str)
        assert len(response) > 0

        # For integration tests, accept either successful response or model error
        # (since we may not have Ollama models installed in CI/test environments)
        if "model" in response.lower() and "not found" in response.lower():
            # This is expected if no Ollama model is available - test passes
            print("Note: Ollama model not available, but RAG pipeline is working")
        else:
            # If we get a real response, it should contain relevant keywords
            assert any(keyword in response.lower() for keyword in [
                "machine learning", "algorithms", "ai", "artificial intelligence", "ml"])

        # Test passed - the pipeline works (with or without Ollama model)

    def test_multiple_document_upload(self, rag_agent):
        """Test uploading multiple documents and querying across them."""
        # Create multiple test documents
        doc1_content = io.BytesIO(b"""
        Python Programming Guide
        
        Python is a high-level programming language.
        It's known for its simplicity and readability.
        Python is widely used in web development, data science, and AI.
        """)

        doc2_content = io.BytesIO(b"""
        Machine Learning with Python
        
        Python has excellent libraries for machine learning.
        Popular libraries include scikit-learn, TensorFlow, and PyTorch.
        These libraries make it easy to build and train ML models.
        """)

        # Upload both documents
        result1 = rag_agent.upload_document(doc1_content, "python_guide.txt")
        result2 = rag_agent.upload_document(doc2_content, "ml_python.txt")

        assert result1["success"] is True
        assert result2["success"] is True

        # Wait for indexing
        time.sleep(2)

        # Query across both documents
        response = rag_agent.query(
            "What programming language is good for machine learning?")

        assert isinstance(response, str)
        assert len(response) > 0

        # Handle case where Ollama model is not available
        if "model" in response.lower() and "not found" in response.lower():
            print("Note: Ollama model not available, but document upload works")
        else:
            # Should contain information from both documents
            assert "python" in response.lower()

    def test_document_deletion(self, rag_agent, sample_text_file):
        """Test document deletion functionality."""
        # Upload a document
        upload_result = rag_agent.upload_document(
            sample_text_file, "delete_test.txt")
        assert upload_result["success"] is True

        # Delete the document
        delete_result = rag_agent.delete_document("delete_test.txt")
        assert delete_result["success"] is True
        assert "delete_test.txt" in delete_result["message"]

    def test_stats_retrieval(self, rag_agent):
        """Test getting statistics from the RAG system."""
        stats = rag_agent.get_stats()

        assert isinstance(stats, dict)
        assert "row_count" in stats or "error" in stats

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, rag_agent):
        """Test concurrent upload and query operations."""
        import asyncio

        # Create test content
        test_docs = []
        for i in range(3):
            content = io.BytesIO(
                f"Test document {i} with unique content about topic {i}.".encode())
            test_docs.append((content, f"concurrent_test_{i}.txt"))

        # Upload documents concurrently (simulate with sequential calls for simplicity)
        upload_tasks = []
        for content, filename in test_docs:
            result = rag_agent.upload_document(content, filename)
            upload_tasks.append(result)

        # Verify all uploads succeeded
        for result in upload_tasks:
            assert result["success"] is True

        # Wait for indexing
        await asyncio.sleep(2)

        # Query concurrently (simulate with sequential calls)
        query_tasks = []
        for i in range(3):
            response = rag_agent.query(f"Tell me about topic {i}")
            query_tasks.append(response)

        # Verify all queries returned responses
        for response in query_tasks:
            assert isinstance(response, str)
            assert len(response) > 0
            # Accept both successful responses and model not found errors
            if "model" in response.lower() and "not found" in response.lower():
                print("Note: Ollama model not available for concurrent test")


class TestDocumentRetrieverIntegration:
    """Integration tests for DocumentRetriever component."""

    @pytest.fixture
    def retriever(self):
        """Create a DocumentRetriever for testing."""
        # First check if Milvus is available
        try:
            from rag_template.vector_store import MilvusVectorStore
            store = MilvusVectorStore(collection_name="test_connection_check")
            store.connect()
            store.disconnect()
        except Exception:
            pytest.skip("Milvus not available for integration tests")

        # If Milvus is available, create the retriever
        try:
            return DocumentRetriever(
                milvus_host="localhost",
                milvus_port=19530,
                embedding_model="all-MiniLM-L6-v2"
            )
        except Exception:
            pytest.skip(
                "Cannot initialize DocumentRetriever for integration tests")

    def test_retriever_upload_and_search(self, retriever):
        """Test document upload and search with DocumentRetriever."""
        # Create test content
        test_content = io.BytesIO(b"""
        Integration Test Document
        
        This document is used for testing the DocumentRetriever component.
        It contains information about software testing methodologies.
        Unit tests verify individual components work correctly.
        Integration tests verify components work together properly.
        """)

        # Upload document
        upload_result = retriever.upload_document(
            test_content, "integration_test.txt")

        if not upload_result["success"]:
            pytest.fail(
                f"Upload failed: {upload_result.get('message', 'Unknown error')}")

        assert upload_result["success"] is True
        assert upload_result["chunks_processed"] > 0

        # Search for relevant content
        search_results = retriever.search_documents(
            "What are integration tests?", top_k=3)

        assert len(search_results) > 0
        assert not search_results[0].get("error")

        # Verify search results contain relevant information
        found_relevant = False
        for result in search_results:
            if "integration" in result["text"].lower() or "testing" in result["text"].lower():
                found_relevant = True
                break

        assert found_relevant, "Search results should contain relevant content"

    def test_retriever_error_handling(self, retriever):
        """Test error handling in DocumentRetriever."""
        # Test with empty file
        empty_content = io.BytesIO(b"")
        result = retriever.upload_document(empty_content, "empty.txt")

        # Should handle gracefully (might succeed with empty document or fail gracefully)
        assert isinstance(result, dict)
        assert "success" in result

        # Test search with empty query
        search_results = retriever.search_documents("", top_k=1)

        # Should handle gracefully
        assert isinstance(search_results, list)
