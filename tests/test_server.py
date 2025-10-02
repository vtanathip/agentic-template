"""Tests for the FastAPI server."""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add src to Python path to import server
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from server.main import app

client = TestClient(app)


class TestServer:
    """Test cases for the FastAPI server."""

    def test_root_endpoint(self):
        """Test the root endpoint returns correct message."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Agentic Template API is running"}

    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["agent"] == "ready"

    def test_chat_endpoint_success(self):
        """Test the chat endpoint with a valid message."""
        test_message = "Hello, agent!"
        response = client.post("/chat", json={"message": test_message})
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "response" in data
        assert "counter" in data
        assert isinstance(data["response"], str)
        assert isinstance(data["counter"], int)
        
        # Check that the response contains processed message
        assert "Processed:" in data["response"]
        assert test_message in data["response"]

    def test_chat_endpoint_empty_message(self):
        """Test the chat endpoint with an empty message."""
        response = client.post("/chat", json={"message": ""})
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "counter" in data

    def test_chat_endpoint_invalid_json(self):
        """Test the chat endpoint with invalid JSON."""
        response = client.post("/chat", json={"invalid": "field"})
        
        # Should return 422 for validation error
        assert response.status_code == 422

    def test_chat_endpoint_missing_message(self):
        """Test the chat endpoint with missing message field."""
        response = client.post("/chat", json={})
        
        # Should return 422 for validation error
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__])