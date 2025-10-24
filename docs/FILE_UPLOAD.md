# File Upload in OpenWebUI Pipeline

## Overview

The LangGraph RAG pipeline now supports file uploads directly from the OpenWebUI chat interface. Users can attach files to their messages, and the pipeline will automatically upload them to the RAG knowledge base.

## How It Works

### Architecture

```
User (OpenWebUI) → Pipeline inlet() → RAG Server /upload → Vector DB
                 ↓
                 Pipeline pipe() → RAG Server /query → Response
```

### Flow

1. **User attaches file** in OpenWebUI chat
2. **inlet() method** intercepts the request
3. **File is downloaded** from OpenWebUI's internal URL
4. **File is uploaded** to RAG server via `/upload` endpoint
5. **Confirmation message** is added to the chat
6. **Normal query flow** continues through `pipe()` method

## Implementation

### Pipeline Method: `inlet()`

The `inlet()` method is called **before** `pipe()` and processes file uploads:

```python
async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
    """Process incoming requests and handle file uploads."""
    messages = body.get("messages", [])
    
    for message in messages:
        if isinstance(message.get("content"), list):
            for content_item in message["content"]:
                if content_item.get("type") == "file":
                    file_url = content_item.get("url", "")
                    
                    # Download file
                    file_response = requests.get(file_url)
                    filename = file_url.split("/")[-1]
                    
                    # Upload to RAG server
                    upload_url = f"{self.valves.RAG_API_URL}/upload"
                    files = {"file": (filename, file_response.content)}
                    upload_response = requests.post(upload_url, files=files)
                    
                    # Add confirmation to message
                    if upload_response.json().get("success"):
                        message["content"] += f"\n\n[File '{filename}' uploaded successfully]"
    
    return body
```

## Usage in OpenWebUI

### 1. Attach a File

In the OpenWebUI chat interface:
1. Click the **paperclip icon** (📎) or attachment button
2. Select a file to upload (PDF, TXT, DOCX, etc.)
3. The file will appear in your message

### 2. Send the Message

Type your message along with the file:
```
Here's a document about machine learning. Can you summarize it?
[Attached: machine_learning.pdf]
```

### 3. Automatic Upload

The pipeline will:
- Detect the attached file
- Upload it to the RAG server
- Process it into the vector database
- Confirm the upload in the chat
- Then answer your question using the newly uploaded document

### 4. Response

You'll see:
```
[File 'machine_learning.pdf' uploaded successfully to knowledge base]

Based on the document you uploaded, here's a summary of machine learning...
```

## Supported File Types

The RAG server supports various document formats:
- **PDF**: `.pdf`
- **Text**: `.txt`
- **Word**: `.docx`
- **Markdown**: `.md`
- **HTML**: `.html`

## Message Format

OpenWebUI sends messages with files in this format:

```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Can you analyze this document?"
        },
        {
          "type": "file",
          "url": "http://openwebui:8080/api/files/abc123/file.pdf"
        }
      ]
    }
  ]
}
```

## Error Handling

### File Download Fails
```
Error processing file: HTTP 404 - File not found
```

### Upload Fails
```
Error uploading file: RAG agent not available
```

### Network Issues
```
Error processing file: Connection timeout
```

## Configuration

### Timeout Settings

Adjust timeouts in the Valves configuration:

```python
class Valves(BaseModel):
    RAG_API_URL: str = "http://rag-api:8001"
    TIMEOUT: int = 120  # Increase for large files
```

### RAG Server URL

The pipeline uses `RAG_API_URL` valve to communicate with the RAG server. Default:
- **Internal (Docker)**: `http://rag-api:8001`
- **External**: `http://localhost:8001`

## Testing

### Manual Test in OpenWebUI

1. Open OpenWebUI: http://localhost:3000
2. Select "LangGraph Agentic RAG" model
3. Click attachment icon
4. Upload a PDF document
5. Type: "What is this document about?"
6. Send and verify:
   - Upload confirmation appears
   - Query response uses the document

### Programmatic Test

Test the upload endpoint directly:

```bash
curl -X POST http://localhost:8001/upload \
  -F "file=@document.pdf"
```

Expected response:
```json
{
  "success": true,
  "message": "Document uploaded successfully",
  "filename": "document.pdf"
}
```

## Debugging

### Check Pipeline Logs

```bash
docker-compose logs -f pipelines
```

Look for:
```
📎 Found file to upload: http://...
📤 Uploading to RAG server: document.pdf
✅ File uploaded successfully: document.pdf
```

### Check RAG Server Logs

```bash
docker-compose logs -f rag-api
```

Look for:
```
INFO: POST /upload - 200 OK
Document uploaded: document.pdf
```

### Common Issues

#### File Not Showing in Knowledge Base

1. Check upload was successful in logs
2. Verify RAG server received the file
3. Check Milvus connection:
   ```bash
   docker-compose logs milvus-standalone
   ```

#### "File URL not accessible"

The pipeline runs in Docker and needs to access OpenWebUI's internal URLs. Ensure:
- Both containers are on the same network (`agentic-network`)
- OpenWebUI is accessible as `http://openwebui:8080` from pipeline container

#### Large File Timeouts

Increase timeout in Valves:
```python
TIMEOUT: int = 300  # 5 minutes for large files
```

## Limitations

1. **File Size**: Limited by FastAPI/Uvicorn defaults (typically ~100MB)
2. **Processing Time**: Large files may take time to process
3. **Concurrent Uploads**: One file at a time per message
4. **File Types**: Only document formats supported by docling library

## Advanced Usage

### Multiple Files

Users can attach multiple files in one message. The pipeline will process them sequentially:

```python
for content_item in message["content"]:
    if content_item.get("type") == "file":
        # Process each file
```

### Custom File Names

The pipeline extracts filenames from URLs. To use custom names, modify the RAG server upload endpoint to accept a filename parameter.

### Progress Indication

For large files, you might want to add progress updates:

```python
# In inlet() method
yield f"Uploading {filename}... {progress}%"
```

## Version History

- **v2.2.0**: Added file upload support via inlet() method
- **v2.1.0**: Synchronized streaming format with RAG server
- **v2.0.0**: RAG-only pipeline with streaming

## Related Documentation

- Pipeline Streaming: `docs/STREAMING_SYNC.md`
- RAG Server API: `src/server/rag_server/README.md`
- OpenWebUI Pipelines: https://docs.openwebui.com/pipelines/

## Example Workflow

1. **Upload a research paper**:
   ```
   User: "Here's a paper on neural networks" [paper.pdf]
   Pipeline: [File 'paper.pdf' uploaded successfully to knowledge base]
   ```

2. **Ask questions**:
   ```
   User: "What are the key findings?"
   Pipeline: [Streams response using the uploaded paper]
   ```

3. **Upload another document**:
   ```
   User: "Compare with this paper" [another_paper.pdf]
   Pipeline: [File 'another_paper.pdf' uploaded successfully to knowledge base]
   Pipeline: [Streams comparison using both papers]
   ```

## Security Considerations

1. **File Validation**: RAG server validates file types
2. **Size Limits**: Prevents abuse with large files
3. **Network Isolation**: Pipeline and RAG server communicate over internal Docker network
4. **No Public URLs**: Files are not exposed to external networks

## Support

For issues with file uploads:
1. Check logs of both pipeline and RAG server
2. Verify network connectivity between containers
3. Test RAG server upload endpoint directly
4. Review RAG server documentation for supported formats
