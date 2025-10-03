"""Unit tests for the multi-agent FastAPI server."""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from src.server.multiagent_api.main import app, AnalysisRequest


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_trading_system():
    """Mock trading system for testing."""
    mock_system = Mock()
    mock_system.analyze_stock.return_value = {
        "ticker": "AAPL",
        "recommendation": "BUY",
        "sentiment_score": 0.8,
        "confidence": 0.9,
        "summary": "Strong buy recommendation for AAPL"
    }
    return mock_system


class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health check returns correct status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "multiagent-api"


class TestRootEndpoint:
    """Test root endpoint."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data
        assert data["version"] == "1.0.0"


class TestAnalysisRequest:
    """Test analysis request model."""

    def test_analysis_request_validation(self):
        """Test analysis request model validation."""
        # Valid request
        request = AnalysisRequest(ticker="AAPL")
        assert request.ticker == "AAPL"
        assert request.stream is True  # default value

        # Request with stream=False
        request = AnalysisRequest(ticker="TSLA", stream=False)
        assert request.ticker == "TSLA"
        assert request.stream is False

        # Invalid request (missing ticker) - this should raise a ValidationError from pydantic
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            AnalysisRequest.model_validate({})


class TestAnalyzeEndpoint:
    """Test stock analysis endpoint."""

    @patch('src.server.multiagent_api.main.TradingSystem')
    def test_analyze_non_streaming(self, mock_trading_class, client, mock_trading_system):
        """Test non-streaming analysis endpoint."""
        mock_trading_class.return_value = mock_trading_system

        response = client.post(
            "/analyze",
            json={"ticker": "AAPL", "stream": False}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ticker"] == "AAPL"
        assert data["recommendation"] == "BUY"
        assert data["sentiment_score"] == 0.8
        assert data["confidence"] == 0.9
        assert "summary" in data

        # Verify trading system was called
        mock_trading_system.analyze_stock.assert_called_once_with("AAPL")

    @patch('src.server.multiagent_api.main.TradingSystem')
    def test_analyze_streaming(self, mock_trading_class, client, mock_trading_system):
        """Test streaming analysis endpoint."""
        # Mock the graph.astream method
        mock_graph = Mock()
        mock_trading_system.graph = mock_graph
        mock_trading_class.return_value = mock_trading_system

        # Mock async iterator for graph.astream
        async def mock_astream(state):
            yield {"news_analysis": {"news_analysis": {"sentiment": 0.5, "confidence": 0.8}}}
            yield {"social_analysis": {"social_analysis": {"sentiment": 0.6, "confidence": 0.7}}}
            yield {"technical_analysis": {"technical_analysis": {"signal": 0.7, "confidence": 0.9}}}
            yield {"synthesize": {"final_recommendation": {
                "ticker": "AAPL",
                "recommendation": "BUY",
                "sentiment_score": 0.8,
                "confidence": 0.9,
                "summary": "Strong buy recommendation"
            }}}

        mock_graph.astream = mock_astream

        response = client.post(
            "/analyze",
            json={"ticker": "AAPL", "stream": True}
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

        # Check that we get streaming response
        content = response.content.decode()
        assert "data:" in content
        assert "analysis_started" in content

    def test_analyze_invalid_ticker(self, client):
        """Test analysis with invalid request."""
        response = client.post(
            "/analyze",
            json={"stream": False}  # Missing ticker
        )

        assert response.status_code == 422  # Validation error

    @patch('src.server.multiagent_api.main.TradingSystem')
    def test_analyze_error_handling(self, mock_trading_class, client):
        """Test error handling in analysis endpoint."""
        mock_trading_system = Mock()
        mock_trading_system.analyze_stock.side_effect = Exception(
            "Analysis failed")
        mock_trading_class.return_value = mock_trading_system

        response = client.post(
            "/analyze",
            json={"ticker": "INVALID", "stream": False}
        )

        assert response.status_code == 500
        data = response.json()
        assert "Analysis failed" in data["detail"]


class TestStreamingResponse:
    """Test streaming response functionality."""

    @patch('src.server.multiagent_api.main.TradingSystem')
    @pytest.mark.asyncio
    async def test_stream_analysis_events(self, mock_trading_class):
        """Test that streaming analysis generates correct events."""
        from src.server.multiagent_api.main import stream_analysis

        # Mock the trading system and graph
        mock_trading_system = Mock()
        mock_graph = Mock()
        mock_trading_system.graph = mock_graph
        mock_trading_class.return_value = mock_trading_system

        # Mock async iterator
        async def mock_astream(state):
            yield {"news_analysis": {"news_analysis": {"sentiment": 0.5}}}
            yield {"synthesize": {"final_recommendation": {
                "ticker": "AAPL",
                "recommendation": "BUY"
            }}}

        mock_graph.astream = mock_astream

        # Collect streaming events
        events = []
        async for event in stream_analysis("AAPL"):
            events.append(event)

        # Verify we got events
        assert len(events) > 0

        # Check for required events
        event_types = []
        for event in events:
            if event.startswith("data: "):
                try:
                    event_data = json.loads(event[6:])
                    event_types.append(event_data.get("event"))
                except json.JSONDecodeError:
                    pass

        assert "analysis_started" in event_types
        assert "stream_complete" in event_types


class TestCORS:
    """Test CORS headers for streaming."""

    @patch('src.server.multiagent_api.main.TradingSystem')
    def test_streaming_cors_headers(self, mock_trading_class, client):
        """Test that streaming response includes CORS headers."""
        mock_trading_system = Mock()
        mock_graph = Mock()
        mock_trading_system.graph = mock_graph
        mock_trading_class.return_value = mock_trading_system

        # Mock async iterator
        async def mock_astream(state):
            yield {"synthesize": {"final_recommendation": {"ticker": "AAPL"}}}

        mock_graph.astream = mock_astream

        response = client.post(
            "/analyze",
            json={"ticker": "AAPL", "stream": True}
        )

        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "*"
        assert "access-control-allow-headers" in response.headers
        assert response.headers["cache-control"] == "no-cache"
        assert response.headers["connection"] == "keep-alive"


if __name__ == "__main__":
    pytest.main([__file__])
