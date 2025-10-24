# RAG Server Streaming Support

## Overview

The RAG server now supports **Server-Sent Events (SSE) streaming** compatible with OpenWebUI pipelines, following the same format as the LangGraph example.

## Changes Made

### 1. Added Streaming Parameter

```python
class QueryRequest(BaseModel):
    query: str
    stream: bool = False  # Default is non-streaming for backward compatibility
```

### 2. Streaming Response Format

The endpoint now returns responses in OpenAI-compatible SSE format:

```
data: {"choices": [{"delta": {"content": "chunk text"}, "finish_reason": null}]}

data: {"choices": [{"delta": {"content": "more text"}, "finish_reason": null}]}

data: {"choices": [{"delta": {}, "finish_reason": "stop"}]}
```

### 3. Dual Mode Support

The `/query` endpoint now supports both modes:

- **Streaming mode** (`stream: true`): Returns `StreamingResponse` with SSE
- **Non-streaming mode** (`stream: false`): Returns JSON response (original behavior)

## Usage

### Streaming Request

```bash
curl -N -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?", "stream": true}'
```

**Response:**
```
data: {"choices": [{"delta": {"content": "Based on the"}, "finish_reason": null}]}

data: {"choices": [{"delta": {"content": " context provided,"}, "finish_reason": null}]}

data: {"choices": [{"delta": {"content": " machine learning"}, "finish_reason": null}]}

data: {"choices": [{"delta": {}, "finish_reason": "stop"}]}
```

### Non-Streaming Request (Original)

```bash
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?", "stream": false}'
```

**Response:**
```json
{
  "response": "Based on the context provided, machine learning is...",
  "success": true,
  "error": null
}
```

## OpenWebUI Pipeline Integration

The streaming format is fully compatible with OpenWebUI pipelines. The pipeline can consume the SSE stream and forward chunks to the frontend:

```python
# In langgraph_pipeline.py
def _stream_rag_response(self, user_message: str, messages: List[dict]):
    data = {
        "query": user_message,
        "stream": True  # Enable streaming
    }
    
    response = requests.post(
        f"{self.valves.RAG_API_URL}/query",
        json=data,
        stream=True
    )
    
    for line in response.iter_lines(decode_unicode=True):
        if line.startswith("data: "):
            chunk = json.loads(line[6:])
            content = chunk["choices"][0]["delta"].get("content", "")
            if content:
                yield content  # Forward to frontend
```

## Implementation Details

### Chunking Strategy

Currently, the response is split into word chunks:
- **Chunk size**: 5 words per chunk
- **Configurable**: Can be adjusted in the code

```python
chunk_size = 5  # words per chunk
words = response.split()

for i in range(0, len(words), chunk_size):
    chunk = ' '.join(words[i:i + chunk_size])
    # Send chunk as SSE...
```

### Error Handling

Errors are also streamed in the same format:

```
data: {"choices": [{"delta": {"content": "Error: connection failed"}, "finish_reason": "error"}]}
```

## Future Enhancements

### 1. True Token-by-Token Streaming

Currently, the RAG agent returns a complete response which is then chunked. For true streaming:

```python
# Modify RAGAgent to support streaming from LLM
class RAGAgent:
    def query_stream(self, query: str):
        """Stream tokens directly from LLM."""
        for token in self.llm.stream(query):
            yield token
```

### 2. Character-Level Chunking

For smoother streaming effect:

```python
chunk_size = 10  # characters per chunk
for i in range(0, len(response), chunk_size):
    chunk = response[i:i + chunk_size]
    yield chunk
```

### 3. Adaptive Chunking

Adjust chunk size based on response length:

```python
if len(response) < 100:
    chunk_size = 5
elif len(response) < 500:
    chunk_size = 10
else:
    chunk_size = 20
```

### 4. Metadata Streaming

Include retrieval metadata in the stream:

```
data: {"choices": [{"delta": {"content": "text", "metadata": {"sources": [...]}}, "finish_reason": null}]}
```

## Testing

### Test Streaming Endpoint

```python
import requests
import json

response = requests.post(
    "http://localhost:8001/query",
    json={"query": "test", "stream": True},
    stream=True
)

for line in response.iter_lines(decode_unicode=True):
    if line.startswith("data: "):
        chunk = json.loads(line[6:])
        print(chunk["choices"][0]["delta"].get("content", ""), end="", flush=True)
```

### Test via OpenWebUI

1. Restart services: `docker-compose restart rag-api pipelines`
2. Open http://localhost:3000
3. Select "LangGraph Agentic RAG" pipeline
4. Ask a question
5. Watch the response stream in real-time! ✨

## Backward Compatibility

✅ **Fully backward compatible**

- Default behavior (`stream: false`) returns JSON response
- Existing clients without `stream` parameter work as before
- No breaking changes to API contract

## Performance Considerations

### Streaming Mode
- **Pros**: 
  - Better perceived performance (users see results immediately)
  - Improved UX with typing effect
  - Works well for long responses
- **Cons**: 
  - Slightly more overhead for HTTP connection
  - Cannot modify response once streaming starts

### Non-Streaming Mode
- **Pros**: 
  - Simpler error handling
  - Can post-process entire response
  - Better for programmatic API clients
- **Cons**: 
  - Higher latency (wait for complete response)
  - Poor UX for long responses

## Related Files

- `src/server/rag_server/app.py` - Main FastAPI server with streaming
- `openwebui/pipelines/langgraph_pipeline.py` - Pipeline consuming the stream
- `src/rag_template/rag_agent.py` - RAG agent (future: add native streaming)

## References

- [OpenWebUI Pipelines Streaming Example](https://github.com/open-webui/pipelines/blob/main/examples/pipelines/integrations/langgraph_pipeline/langgraph_example.py)
- [Server-Sent Events (SSE) Specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [OpenAI Streaming API Format](https://platform.openai.com/docs/api-reference/streaming)
