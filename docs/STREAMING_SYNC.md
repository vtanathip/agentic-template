# Streaming Format Synchronization

## Overview
This document describes the synchronization between the RAG FastAPI server (`src/server/rag_server/app.py`) and the OpenWebUI pipeline (`openwebui/pipelines/langgraph_pipeline.py`) for streaming responses.

## Format Specification

### RAG Server Output Format (SSE/Server-Sent Events)

The RAG server uses **OpenAI-compatible streaming format** when `stream=true`:

```json
data: {"choices": [{"delta": {"content": "text chunk"}, "finish_reason": null}]}

data: {"choices": [{"delta": {"content": " more text"}, "finish_reason": null}]}

data: {"choices": [{"delta": {}, "finish_reason": "stop"}]}
```

### Structure

```json
{
    "choices": [
        {
            "delta": {
                "content": "text chunk"  // The actual text content
            },
            "finish_reason": null | "stop" | "error"
        }
    ]
}
```

### Fields

- **choices**: Array containing the response (always has 1 element)
- **delta**: Object containing the incremental content
  - **content**: The text chunk to display (string)
- **finish_reason**: Indicates streaming status
  - `null`: More chunks coming
  - `"stop"`: Streaming completed successfully
  - `"error"`: An error occurred

## Pipeline Parsing Logic

The pipeline (`langgraph_pipeline.py`) parses the SSE stream as follows:

```python
# 1. Strip "data: " prefix from SSE format
if line.startswith("data: "):
    line = line[6:]

# 2. Parse JSON
chunk = json.loads(line)

# 3. Extract content using OpenAI format (primary)
if "choices" in chunk and isinstance(chunk["choices"], list) and len(chunk["choices"]) > 0:
    choice = chunk["choices"][0]
    if "delta" in choice and isinstance(choice["delta"], dict):
        content = choice["delta"].get("content", "")
        if content:
            yield content  # Stream to frontend
```

## Implementation Details

### RAG Server (`app.py`)

```python
@app.post("/query")
async def query_documents(request: QueryRequest):
    if request.stream:
        async def stream_response():
            response = rag_agent.query(request.query)
            
            # Split into chunks
            words = response.split()
            for i in range(0, len(words), chunk_size):
                chunk = ' '.join(words[i:i + chunk_size])
                
                # Send in OpenAI format
                chunk_msg = {
                    'choices': [{
                        'delta': {'content': chunk},
                        'finish_reason': None
                    }]
                }
                yield f"data: {json.dumps(chunk_msg)}\n\n"
            
            # Send completion
            end_msg = {
                'choices': [{
                    'delta': {},
                    'finish_reason': 'stop'
                }]
            }
            yield f"data: {json.dumps(end_msg)}\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
```

### Pipeline (`langgraph_pipeline.py`)

```python
def _stream_rag_response(self, user_message: str, messages: List[dict]):
    data = {"query": user_message, "stream": True}
    response = requests.post(url, json=data, stream=True)
    
    for line in response.iter_lines(decode_unicode=True):
        if line.startswith("data: "):
            line = line[6:]
        
        chunk = json.loads(line)
        
        # Primary: OpenAI format
        if "choices" in chunk:
            choice = chunk["choices"][0]
            if "delta" in choice:
                content = choice["delta"].get("content", "")
                if content:
                    yield content
```

## Backward Compatibility

The pipeline also supports legacy formats for backward compatibility:

```python
# Legacy format support
elif "content" in chunk:
    yield chunk["content"]
elif "chunk" in chunk:
    yield chunk["chunk"]
elif "response" in chunk:
    yield chunk["response"]
elif "text" in chunk:
    yield chunk["text"]
```

## Testing

Run synchronization tests to verify format compatibility:

```bash
uv run pytest tests/test_streaming_sync.py -v
```

Tests verify:
1. ✅ RAG server produces correct OpenAI-compatible format
2. ✅ Pipeline can parse the format correctly
3. ✅ Finish reasons are handled properly
4. ✅ Error states are communicated correctly
5. ✅ Backward compatibility is maintained

## Why OpenAI-Compatible Format?

This format was chosen because:

1. **Industry Standard**: OpenAI's streaming format is widely recognized
2. **Tool Compatibility**: Many tools expect this format
3. **Future-Proof**: Easy to integrate with other OpenAI-compatible services
4. **Rich Metadata**: Supports finish reasons, roles, and other metadata
5. **Extensible**: Can add more fields without breaking existing code

## Request Format

### Streaming Request
```json
{
    "query": "What is the meaning of life?",
    "stream": true
}
```

### Non-Streaming Request
```json
{
    "query": "What is the meaning of life?",
    "stream": false
}
```

## Response Examples

### Streaming Response (SSE)
```
data: {"choices": [{"delta": {"content": "The meaning of"}, "finish_reason": null}]}

data: {"choices": [{"delta": {"content": " life is"}, "finish_reason": null}]}

data: {"choices": [{"delta": {"content": " 42."}, "finish_reason": null}]}

data: {"choices": [{"delta": {}, "finish_reason": "stop"}]}
```

### Non-Streaming Response (JSON)
```json
{
    "response": "The meaning of life is 42.",
    "success": true,
    "error": null
}
```

## Error Handling

### Server Error
```json
data: {"choices": [{"delta": {"content": "Error: Database connection failed"}, "finish_reason": "error"}]}
```

### Pipeline Handling
```python
if choice.get("finish_reason") == "error":
    # Log error and stop streaming
    continue
```

## Version History

- **v2.1.0** (Current): Synchronized with OpenAI-compatible SSE format
- **v2.0.0**: RAG-only pipeline with initial streaming support
- **v1.0.0**: Dual-mode (agentic/RAG) pipeline

## Files Modified

1. `src/server/rag_server/app.py`
   - Added OpenAI-compatible SSE format documentation
   - Already implemented in v1.0

2. `openwebui/pipelines/langgraph_pipeline.py`
   - Updated to prioritize OpenAI format parsing
   - Added comprehensive format documentation
   - Version bumped to 2.1.0

3. `tests/test_streaming_sync.py`
   - New test suite to verify synchronization
   - Tests both formats and error handling

## Maintenance Notes

When updating streaming logic:

1. **Keep formats in sync**: Changes to RAG server format must be reflected in pipeline
2. **Test both ends**: Run `test_streaming_sync.py` after changes
3. **Document changes**: Update this file with any format modifications
4. **Version bump**: Increment pipeline version when changing format

## Related Documentation

- RAG Server Streaming: `src/server/rag_server/STREAMING_SUPPORT.md`
- Pipeline Architecture: `openwebui/ARCHITECTURE_RAG.md` (if exists)
- OpenWebUI Pipeline Docs: Official OpenWebUI documentation
- OpenAI Streaming API: https://platform.openai.com/docs/api-reference/streaming

## Contact

For questions about streaming format:
- Author: vtanathip
- GitHub: https://github.com/vtanathip/agentic-template
- File an issue if you find synchronization problems
