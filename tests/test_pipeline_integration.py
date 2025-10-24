"""
Integration test for OpenWebUI Pipeline with actual APIs.

Prerequisites:
1. Agentic API must be running on port 8000
2. RAG API must be running on port 8001 (optional for RAG tests)

Run: uv run pytest tests/test_pipeline_integration.py -v -s
"""

import pytest
import requests
from openwebui.langgraph_pipeline import Pipeline


def is_api_running(url: str) -> bool:
    """Check if an API is accessible."""
    try:
        response = requests.get(f"{url}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


@pytest.mark.skipif(
    not is_api_running("http://localhost:8000"),
    reason="Agentic API not running on port 8000"
)
def test_pipeline_with_real_agentic_api():
    """Test pipeline with actual Agentic Template API."""
    pipeline = Pipeline()

    messages = [
        {"role": "user", "content": "Hello from integration test"}
    ]
    body = {"stream": False}

    result = pipeline.pipe("Hello from integration test",
                           "model", messages, body)

    print(f"\n✓ Agentic API Response: {result}")

    # Should get a response back
    assert isinstance(result, str)
    assert len(result) > 0
    # The agent echoes messages with "Processed:" prefix
    assert "Processed:" in result or "Hello" in result


@pytest.mark.skipif(
    not is_api_running("http://localhost:8000"),
    reason="Agentic API not running on port 8000"
)
def test_pipeline_with_real_agentic_api_streaming():
    """Test pipeline with actual Agentic Template API in streaming mode."""
    pipeline = Pipeline()

    messages = [
        {"role": "user", "content": "Stream test"}
    ]
    body = {"stream": True}

    result = pipeline.pipe("Stream test", "model", messages, body)

    # Should get an iterator
    assert hasattr(result, '__iter__')

    # Try to get at least one chunk
    chunks = []
    try:
        for i, chunk in enumerate(result):
            if i < 5:  # Only get first 5 chunks
                chunks.append(chunk)
            else:
                break
    except StopIteration:
        pass

    print(f"\n✓ Streaming API Response ({len(chunks)} chunks received)")
    if chunks:
        print(f"  First chunk: {chunks[0]}")

    # We should have received at least one chunk
    assert len(chunks) > 0


@pytest.mark.skipif(
    not is_api_running("http://localhost:8001"),
    reason="RAG API not running on port 8001"
)
def test_pipeline_with_real_rag_api():
    """Test pipeline with actual RAG Template API."""
    pipeline = Pipeline()
    pipeline.valves.USE_RAG = True

    messages = [
        {"role": "user", "content": "What documents are available?"}
    ]
    body = {}

    result = pipeline.pipe(
        "What documents are available?", "model", messages, body)

    print(f"\n✓ RAG API Response: {result}")

    # Should get a response back
    assert isinstance(result, str)
    assert len(result) > 0


def test_pipeline_health_checks():
    """Test that we can check API health before using pipeline."""
    agentic_running = is_api_running("http://localhost:8000")
    rag_running = is_api_running("http://localhost:8001")

    print(f"\n✓ API Status:")
    print(
        f"  Agentic API (port 8000): {'✓ Running' if agentic_running else '✗ Not Running'}")
    print(
        f"  RAG API (port 8001): {'✓ Running' if rag_running else '✗ Not Running'}")

    # This test always passes, just for info
    assert True


def test_pipeline_configuration_validation():
    """Test that pipeline configuration is valid."""
    pipeline = Pipeline()

    # Check default configuration
    assert pipeline.valves.AGENTIC_API_URL == "http://localhost:8000"
    assert pipeline.valves.RAG_API_URL == "http://localhost:8001"
    assert pipeline.valves.USE_RAG is False
    assert pipeline.valves.TIMEOUT == 120

    # Test configuration changes
    pipeline.valves.TIMEOUT = 60
    assert pipeline.valves.TIMEOUT == 60

    pipeline.valves.USE_RAG = True
    assert pipeline.valves.USE_RAG is True

    print("\n✓ Pipeline configuration is valid")


if __name__ == "__main__":
    # Run with verbose output
    pytest.main([__file__, "-v", "-s"])
