"""Tests for the FastAPI server."""

import pytest
from fastapi.testclient import TestClient

from server.main import app


client = TestClient(app)


class TestServer:
    """Test cases for the FastAPI server."""

    def test_root_endpoint(self):
        """Test the root endpoint returns correct message."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {
            "message": "Agentic Template API is running"}

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

    def test_openai_models_endpoint(self):
        """Test the OpenAI-compatible models endpoint."""
        response = client.get("/v1/models")

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "object" in data
        assert "data" in data
        assert data["object"] == "list"
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

        # Check model info
        model = data["data"][0]
        assert model["id"] == "agentic-template"
        assert model["object"] == "model"

    def test_openai_chat_completions_endpoint(self):
        """Test the OpenAI-compatible chat completions endpoint."""
        test_request = {
            "model": "agentic-template",
            "messages": [
                {"role": "user", "content": "Hello, how are you?"}
            ]
        }

        response = client.post("/v1/chat/completions", json=test_request)

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "id" in data
        assert "object" in data
        assert "created" in data
        assert "model" in data
        assert "choices" in data
        assert "usage" in data

        # Check specific values
        assert data["object"] == "chat.completion"
        assert data["model"] == "agentic-template"
        assert len(data["choices"]) == 1

        # Check choice structure
        choice = data["choices"][0]
        assert "index" in choice
        assert "message" in choice
        assert "finish_reason" in choice

        # Check message structure
        message = choice["message"]
        assert message["role"] == "assistant"
        assert isinstance(message["content"], str)
        assert len(message["content"]) > 0

    def test_openai_chat_completions_no_user_message(self):
        """Test the OpenAI chat completions endpoint with no user message."""
        test_request = {
            "model": "agentic-template",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant"}
            ]
        }

        response = client.post("/v1/chat/completions", json=test_request)

        # Should return 400 for no user message
        assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__])
