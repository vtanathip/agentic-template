"""
Unit tests for the RAG server FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import io
from server.rag_server.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_rag_agent():
    """Create a mock RAG agent for testing."""
    mock_agent = Mock()

    # Mock successful upload
    mock_agent.upload_document.return_value = {
        "success": True,
        "message": "Successfully uploaded test.txt. Processed 5 chunks with 500 total characters.",
        "filename": "test.txt"
    }

    # Mock successful query
    mock_agent.query.return_value = "This is a test response from the RAG agent."

    # Mock stats
    mock_agent.get_stats.return_value = {
        "total_documents": 1,
        "total_chunks": 5,
        "collection_size": 500
    }

    # Mock delete document
    mock_agent.delete_document.return_value = {
        "success": True,
        "message": "Document deleted successfully"
    }

    return mock_agent


class TestHealthEndpoints:
    """Test health and status endpoints."""

    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "RAG Agent API is running"
        assert data["status"] == "healthy"

    def test_health_check_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "rag_agent" in data
        assert data["version"] == "1.0.0"


class TestDocumentUpload:
    """Test document upload functionality."""

    def test_upload_document_success(self, client, mock_rag_agent):
        """Test successful document upload."""
        with patch('server.rag_server.app.rag_agent', mock_rag_agent):
            # Create test file
            test_content = b"This is test document content for upload."
            test_file = ("test.txt", io.BytesIO(test_content), "text/plain")

            response = client.post(
                "/upload",
                files={"file": test_file}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["filename"] == "test.txt"
            assert "Successfully uploaded" in data["message"]

    def test_upload_document_failure(self, client):
        """Test document upload failure."""
        # Mock failed upload
        mock_agent = Mock()
        mock_agent.upload_document.return_value = {
            "success": False,
            "message": "Failed to process document",
            "filename": "test.txt"
        }

        with patch('server.rag_server.app.rag_agent', mock_agent):
            test_content = b"This is test document content."
            test_file = ("test.txt", io.BytesIO(test_content), "text/plain")

            response = client.post(
                "/upload",
                files={"file": test_file}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert data["error"] == "Failed to process document"

    def test_upload_without_rag_agent(self, client):
        """Test upload when RAG agent is not available."""
        with patch('server.rag_server.app.rag_agent', None):
            test_content = b"This is test content."
            test_file = ("test.txt", io.BytesIO(test_content), "text/plain")

            response = client.post(
                "/upload",
                files={"file": test_file}
            )

            assert response.status_code == 503
            assert "RAG agent not available" in response.json()["detail"]


class TestDocumentQuery:
    """Test document querying functionality."""

    def test_query_success(self, client, mock_rag_agent):
        """Test successful document query."""
        with patch('server.rag_server.app.rag_agent', mock_rag_agent):
            query_data = {"query": "What is the main topic?"}

            response = client.post("/query", json=query_data)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["response"] == "This is a test response from the RAG agent."
            assert data["error"] is None

    def test_query_with_error_response(self, client):
        """Test query with error response from RAG agent."""
        mock_agent = Mock()
        mock_agent.query.return_value = "Error: No relevant documents found"

        with patch('server.rag_server.app.rag_agent', mock_agent):
            query_data = {"query": "What is the main topic?"}

            response = client.post("/query", json=query_data)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert data["error"] == "Error: No relevant documents found"

    def test_query_without_rag_agent(self, client):
        """Test query when RAG agent is not available."""
        with patch('server.rag_server.app.rag_agent', None):
            query_data = {"query": "What is the main topic?"}

            response = client.post("/query", json=query_data)

            assert response.status_code == 503
            assert "RAG agent not available" in response.json()["detail"]

    def test_query_invalid_data(self, client):
        """Test query with invalid data."""
        response = client.post("/query", json={"invalid": "data"})

        assert response.status_code == 422  # Validation error


class TestStatsEndpoint:
    """Test statistics endpoint."""

    def test_get_stats_success(self, client, mock_rag_agent):
        """Test successful stats retrieval."""
        with patch('server.rag_server.app.rag_agent', mock_rag_agent):
            response = client.get("/stats")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "stats" in data
            assert data["stats"]["total_documents"] == 1
            assert data["stats"]["total_chunks"] == 5

    def test_get_stats_without_rag_agent(self, client):
        """Test stats when RAG agent is not available."""
        with patch('server.rag_server.app.rag_agent', None):
            response = client.get("/stats")

            assert response.status_code == 503
            assert "RAG agent not available" in response.json()["detail"]


class TestDocumentDeletion:
    """Test document deletion functionality."""

    def test_delete_document_success(self, client, mock_rag_agent):
        """Test successful document deletion."""
        with patch('server.rag_server.app.rag_agent', mock_rag_agent):
            response = client.delete("/documents/test.txt")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["filename"] == "test.txt"
            assert "successfully" in data["message"].lower()

    def test_delete_document_without_rag_agent(self, client):
        """Test deletion when RAG agent is not available."""
        with patch('server.rag_server.app.rag_agent', None):
            response = client.delete("/documents/test.txt")

            assert response.status_code == 503
            assert "RAG agent not available" in response.json()["detail"]


@pytest.mark.asyncio
class TestAsyncBehavior:
    """Test async behavior and error handling."""

    async def test_concurrent_requests(self, client, mock_rag_agent):
        """Test handling multiple concurrent requests."""
        with patch('server.rag_server.app.rag_agent', mock_rag_agent):
            # Test multiple queries concurrently
            query_data = {"query": "Test concurrent query"}

            # Simulate multiple requests (using sync client for simplicity)
            responses = []
            for _ in range(3):
                response = client.post("/query", json=query_data)
                responses.append(response)

            # All requests should succeed
            for response in responses:
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True


if __name__ == "__main__":
    pytest.main([__file__])
