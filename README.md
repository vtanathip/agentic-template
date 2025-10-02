# agentic-template
Starter Kit for Building AI Agents with LangChain

## Overview

This is a simple LangGraph agent implementation using UV as the package manager. It includes:
- A basic LangGraph agent that processes messages
- Unit tests for the agent
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

Run the example agent:
```bash
uv run python main.py
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

