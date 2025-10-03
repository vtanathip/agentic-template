# Multi-Agent Trading System API

A FastAPI server that provides streaming access to the multi-agent trading system for stock analysis. This server is designed to work seamlessly with OpenWebUI and other web-based clients.

## Features

- **Streaming Response**: Real-time streaming of analysis progress using Server-Sent Events (SSE)
- **Multi-Agent Analysis**: Integrates news, social, and technical analysis agents
- **OpenWebUI Compatible**: Designed for integration with OpenWebUI tool
- **Minimal Dependencies**: Uses only essential FastAPI and Pydantic components
- **Full Test Coverage**: Comprehensive pytest test suite included

## API Endpoints

### Health Check
```
GET /health
```
Returns the health status of the API.

### Stock Analysis
```
POST /analyze
```
Analyzes a stock using the multi-agent system.

**Request Body:**
```json
{
  "ticker": "AAPL",
  "stream": true
}
```

**Parameters:**
- `ticker` (string, required): Stock ticker symbol to analyze
- `stream` (boolean, optional): Whether to stream the response (default: true)

### Root Information
```
GET /
```
Returns API information and available endpoints.

## Streaming Response Format

When `stream=true`, the API returns Server-Sent Events with the following event types:

- `analysis_started`: Analysis has begun
- `analysis_progress`: Progress updates during execution
- `news_analysis_complete`: News analysis results available
- `social_analysis_complete`: Social analysis results available  
- `technical_analysis_complete`: Technical analysis results available
- `analysis_complete`: Final recommendation ready
- `stream_complete`: Analysis stream finished
- `error`: Error occurred during analysis

### Example Event
```
data: {"event": "analysis_complete", "data": {"ticker": "AAPL", "result": {"recommendation": "BUY", "confidence": 0.9}}}
```

## Usage

### Starting the Server

Using uv (recommended):
```bash
uv run python -m src.server.multiagent_api.main
```

Using uvicorn directly:
```bash
uvicorn src.server.multiagent_api.main:app --host 0.0.0.0 --port 8000
```

### Testing with curl

Non-streaming request:
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "stream": false}'
```

Streaming request:
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "stream": true}'
```

### Integration with OpenWebUI

This API is designed to work with OpenWebUI as a tool. The streaming response format provides real-time updates that can be displayed in the OpenWebUI interface.

## Development

### Running Tests

```bash
# Run all tests
uv run pytest src/server/multiagent_api/test_multiagent_api.py

# Run with coverage
uv run pytest src/server/multiagent_api/test_multiagent_api.py --cov=src.server.multiagent_api

# Run specific test class
uv run pytest src/server/multiagent_api/test_multiagent_api.py::TestAnalyzeEndpoint
```

### Test Coverage

The test suite covers:
- Health check endpoint
- Root endpoint information
- Request/response model validation
- Both streaming and non-streaming analysis
- Error handling
- CORS headers for web integration
- Streaming event generation

### Dependencies

The server uses these minimal dependencies:
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `pydantic`: Data validation
- `langchain-core`: For message handling

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   OpenWebUI     │────│  FastAPI Server  │────│ Multi-Agent     │
│   Client        │    │  (multiagent_api)│    │ Trading System  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                          │
                              │                          ▼
                              │                  ┌─────────────────┐
                              └──────────────────► News Agent      │
                                                 │ Social Agent    │
                                                 │ Technical Agent │
                                                 └─────────────────┘
```

## Configuration

The server runs on:
- **Host**: 0.0.0.0 (configurable)
- **Port**: 8000 (configurable)
- **Environment**: Development/Production ready

## Error Handling

The API includes comprehensive error handling:
- Input validation errors (422)
- Analysis execution errors (500)
- Proper error messages in both streaming and non-streaming modes

## CORS Support

The streaming endpoints include CORS headers for web browser compatibility:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Headers: *`
- `Cache-Control: no-cache`
- `Connection: keep-alive`