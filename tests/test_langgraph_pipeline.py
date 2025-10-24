"""
Simple test for LangGraph OpenWebUI Pipeline.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from openwebui.langgraph_pipeline import Pipeline


def test_pipeline_initialization():
    """Test that the pipeline initializes correctly."""
    pipeline = Pipeline()

    assert pipeline.id == "langgraph_agentic_template"
    assert pipeline.name == "LangGraph Agentic Template"
    assert pipeline.valves is not None
    assert pipeline.valves.AGENTIC_API_URL == "http://localhost:8000"
    assert pipeline.valves.RAG_API_URL == "http://localhost:8001"
    assert pipeline.valves.USE_RAG is False
    assert pipeline.valves.TIMEOUT == 120


@pytest.mark.asyncio
async def test_on_startup():
    """Test the on_startup callback."""
    pipeline = Pipeline()
    # Should not raise any exceptions
    await pipeline.on_startup()


@pytest.mark.asyncio
async def test_on_shutdown():
    """Test the on_shutdown callback."""
    pipeline = Pipeline()
    # Should not raise any exceptions
    await pipeline.on_shutdown()


@pytest.mark.asyncio
async def test_on_valves_updated():
    """Test the on_valves_updated callback."""
    pipeline = Pipeline()
    # Should not raise any exceptions
    await pipeline.on_valves_updated()


def test_pipe_agentic_non_streaming():
    """Test the pipe method with agentic API in non-streaming mode."""
    pipeline = Pipeline()

    messages = [
        {"role": "user", "content": "Hello"}
    ]
    body = {"stream": False}

    # Mock the requests.post response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Processed: Hello"
                }
            }
        ]
    }
    mock_response.raise_for_status = Mock()

    with patch('requests.post', return_value=mock_response) as mock_post:
        result = pipeline.pipe("Hello", "model-id", messages, body)

        # Verify the request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args

        assert call_args[1]['json']['model'] == 'agentic-template'
        assert call_args[1]['json']['stream'] is False
        assert len(call_args[1]['json']['messages']) == 1
        assert call_args[1]['json']['messages'][0]['content'] == 'Hello'

        # Verify the result
        assert result == "Processed: Hello"


def test_pipe_agentic_streaming():
    """Test the pipe method with agentic API in streaming mode."""
    pipeline = Pipeline()

    messages = [
        {"role": "user", "content": "Hello"}
    ]
    body = {"stream": True}

    # Mock the streaming response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.iter_lines.return_value = iter([
        b'data: {"choices": [{"delta": {"content": "Hello"}}]}',
        b'data: {"choices": [{"delta": {"content": " there"}}]}',
        b'data: [DONE]'
    ])
    mock_response.raise_for_status = Mock()

    with patch('requests.post', return_value=mock_response) as mock_post:
        result = pipeline.pipe("Hello", "model-id", messages, body)

        # Verify the request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args

        assert call_args[1]['json']['stream'] is True
        assert call_args[1]['stream'] is True

        # Verify we got an iterator back
        assert hasattr(result, '__iter__')


def test_pipe_rag_mode():
    """Test the pipe method with RAG API."""
    pipeline = Pipeline()
    pipeline.valves.USE_RAG = True

    messages = [
        {"role": "user", "content": "What is in the documents?"}
    ]
    body = {}

    # Mock the RAG API response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "response": "Based on the documents, here is the answer..."
    }
    mock_response.raise_for_status = Mock()

    with patch('requests.post', return_value=mock_response) as mock_post:
        result = pipeline.pipe("What is in the documents?",
                               "model-id", messages, body)

        # Verify the request was made to RAG API
        mock_post.assert_called_once()
        call_args = mock_post.call_args

        assert 'localhost:8001' in call_args[0][0]
        assert call_args[1]['json']['query'] == 'What is in the documents?'

        # Verify the result
        assert result == "Based on the documents, here is the answer..."


def test_pipe_rag_mode_error():
    """Test the pipe method with RAG API error."""
    pipeline = Pipeline()
    pipeline.valves.USE_RAG = True

    messages = [
        {"role": "user", "content": "Query"}
    ]
    body = {}

    # Mock the RAG API error response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": False,
        "error": "No documents found"
    }
    mock_response.raise_for_status = Mock()

    with patch('requests.post', return_value=mock_response) as mock_post:
        result = pipeline.pipe("Query", "model-id", messages, body)

        # Verify error message is returned
        assert "RAG Error:" in result
        assert "No documents found" in result


def test_pipe_connection_error():
    """Test the pipe method with connection error."""
    pipeline = Pipeline()

    messages = [
        {"role": "user", "content": "Hello"}
    ]
    body = {}

    # Mock a connection error
    with patch('requests.post', side_effect=Exception("Connection refused")):
        result = pipeline.pipe("Hello", "model-id", messages, body)

        # Verify error message is returned
        assert "Error in pipeline:" in result
        assert "Connection refused" in result


def test_valves_configuration():
    """Test that valves can be configured."""
    pipeline = Pipeline()

    # Update valves
    pipeline.valves.AGENTIC_API_URL = "http://custom-host:9000"
    pipeline.valves.USE_RAG = True
    pipeline.valves.TIMEOUT = 60

    assert pipeline.valves.AGENTIC_API_URL == "http://custom-host:9000"
    assert pipeline.valves.USE_RAG is True
    assert pipeline.valves.TIMEOUT == 60


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
