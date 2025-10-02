# agentic-template
Starter Kit for Building AI Agents with LangChain

## Overview

This is a simple LangGraph agent implementation using UV as the package manager. It includes:
- A basic LangGraph agent that processes messages
- FastAPI server to expose the agent via REST API
- Unit tests for both the agent and server
- GitHub Actions workflow for automated testing
- LangGraph Studio configuration

## Prerequisites

- Python 3.12+
- UV package manager

## Installation

1. Install UV (if not already installed):
```bash
pip install uv
```

2. Clone the repository and install dependencies:
```bash
git clone https://github.com/vtanathip/agentic-template.git
cd agentic-template
uv sync --dev
```

## Usage

### Running the Agent Directly
Run the example agent:
```bash
uv run python main.py
```

### Running the FastAPI Server
Start the FastAPI server to interact with the agent via REST API:
```bash
uv run python run_server.py
```

The server will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Running with Docker + OpenWebUI
Start the full stack with OpenWebUI chat interface:
```bash
cd docker
docker-compose up --build -d
```

This will start:
- FastAPI server at http://localhost:8000
- OpenWebUI chat interface at http://localhost:3000

See `docker/README.md` for detailed Docker setup instructions.

#### API Endpoints

**POST /chat**
Send a message to the agent:
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, agent!"}'
```

Response:
```json
{
  "response": "Processed: Hello, agent!",
  "counter": 1
}
```

## Testing

Run the test suite:
```bash
uv run pytest tests/ -v
```

## LangGraph Studio

This project includes a `langgraph.json` configuration file for use with LangGraph Studio. Open the project in LangGraph Studio to visualize and interact with the agent graph.

## Project Structure

```
.
├── src/
│   └── agentic_template/
│       ├── __init__.py
│       └── agent.py          # LangGraph agent implementation
├── tests/
│   └── test_agent.py         # Unit tests
├── .github/
│   └── workflows/
│       └── test.yml          # GitHub Actions workflow
├── main.py                   # Example usage
├── pyproject.toml            # Project dependencies
└── langgraph.json            # LangGraph Studio config
```

## License

MIT License - see LICENSE file for details.

