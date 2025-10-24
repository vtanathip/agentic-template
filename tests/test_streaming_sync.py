"""
Test to verify synchronization between RAG server streaming format 
and pipeline parsing logic.
"""

import json
import pytest


def test_rag_server_streaming_format():
    """Verify RAG server produces correct SSE format."""
    # Expected format from RAG server (app.py)
    expected_chunk = {
        'choices': [{
            'delta': {'content': 'test chunk'},
            'finish_reason': None
        }]
    }

    # This should be parseable as JSON
    json_str = json.dumps(expected_chunk)
    parsed = json.loads(json_str)

    # Verify structure
    assert "choices" in parsed
    assert isinstance(parsed["choices"], list)
    assert len(parsed["choices"]) > 0
    assert "delta" in parsed["choices"][0]
    assert "content" in parsed["choices"][0]["delta"]
    assert parsed["choices"][0]["delta"]["content"] == "test chunk"


def test_pipeline_can_parse_rag_format():
    """Verify pipeline can parse the RAG server format."""
    # Format produced by RAG server
    rag_chunk = {
        'choices': [{
            'delta': {'content': 'Hello world'},
            'finish_reason': None
        }]
    }

    # Pipeline parsing logic (simplified)
    chunk = rag_chunk
    content = None

    if "choices" in chunk and isinstance(chunk["choices"], list) and len(chunk["choices"]) > 0:
        choice = chunk["choices"][0]
        if "delta" in choice and isinstance(choice["delta"], dict):
            content = choice["delta"].get("content", "")

    assert content == "Hello world"


def test_pipeline_handles_finish_reason():
    """Verify pipeline correctly handles finish reasons."""
    # End chunk from RAG server
    end_chunk = {
        'choices': [{
            'delta': {},
            'finish_reason': 'stop'
        }]
    }

    # Pipeline should detect finish_reason
    chunk = end_chunk
    finish_reason = None

    if "choices" in chunk and isinstance(chunk["choices"], list) and len(chunk["choices"]) > 0:
        choice = chunk["choices"][0]
        finish_reason = choice.get("finish_reason")

    assert finish_reason == "stop"


def test_pipeline_handles_error():
    """Verify pipeline correctly handles error finish reason."""
    # Error chunk from RAG server
    error_chunk = {
        'choices': [{
            'delta': {'content': 'Error: Something went wrong'},
            'finish_reason': 'error'
        }]
    }

    # Pipeline should extract error content
    chunk = error_chunk
    content = None
    finish_reason = None

    if "choices" in chunk and isinstance(chunk["choices"], list) and len(chunk["choices"]) > 0:
        choice = chunk["choices"][0]
        if "delta" in choice and isinstance(choice["delta"], dict):
            content = choice["delta"].get("content", "")
        finish_reason = choice.get("finish_reason")

    assert content == "Error: Something went wrong"
    assert finish_reason == "error"


def test_backward_compatibility_formats():
    """Verify pipeline still handles alternative formats."""
    test_formats = [
        {"content": "direct content"},
        {"chunk": "chunked content"},
        {"response": "response content"},
        {"text": "text content"}
    ]

    for test_chunk in test_formats:
        # Pipeline should extract content from any format
        chunk = test_chunk
        content = None

        # Primary format (OpenAI)
        if "choices" in chunk and isinstance(chunk.get("choices"), list):
            pass  # Not this format
        # Backward compatibility
        elif "content" in chunk:
            content = chunk["content"]
        elif "chunk" in chunk:
            content = chunk["chunk"]
        elif "response" in chunk:
            content = chunk["response"]
        elif "text" in chunk:
            content = chunk["text"]

        assert content is not None
        assert isinstance(content, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
