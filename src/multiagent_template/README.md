# Multi-Agent Trading System

A minimal multi-agent system for stock market analysis using LangGraph. This system coordinates three specialized agents to provide comprehensive trading recommendations.

## Overview

The trading system consists of three agents:

1. **NewsAgent** - Analyzes market news and sentiment
2. **SocialAgent** - Monitors social media discussions and sentiment  
3. **TechnicalAgent** - Performs technical analysis of price movements

## Architecture

```
TradingSystem
├── NewsAgent (News & Sentiment Analysis)
├── SocialAgent (Social Media Analysis)  
├── TechnicalAgent (Technical Analysis)
└── Synthesizer (Final Recommendation)
```

## Quick Start

```python
from src.multiagent_template import TradingSystem

# Create trading system
trading_system = TradingSystem()

# Analyze a stock
recommendation = trading_system.analyze_stock("AAPL")
print(f"Recommendation: {recommendation['recommendation']}")
print(f"Confidence: {recommendation['confidence']}")
```

## Example Usage

Run the example:

```bash
# Run the example
uv run python -m src.multiagent_template.example

# Or use the CLI interface
uv run python -m src.multiagent_template.main AAPL TSLA

# Multiple stocks with JSON output
uv run python -m src.multiagent_template.main AAPL TSLA MSFT --json
```

## Components

### TradingSystem
The main orchestrator that coordinates all agents and synthesizes their results into a final recommendation.

### Agents

#### NewsAgent
- Analyzes market news sentiment
- Provides sentiment score (-1 to 1)
- Identifies key topics and trends

#### SocialAgent  
- Monitors social media sentiment
- Tracks discussion volume
- Analyzes sentiment across platforms

#### TechnicalAgent
- Performs technical indicator analysis
- Generates buy/sell/hold signals
- Calculates trend direction

## State Management

The system uses a shared state object that flows between agents:

```python
class TradingState(TypedDict):
    ticker: str
    messages: List[BaseMessage]
    news_analysis: Dict[str, Any]
    social_analysis: Dict[str, Any]
    technical_analysis: Dict[str, Any]
    final_recommendation: Dict[str, Any]
```

## Output Format

Each analysis returns a structured recommendation:

```python
{
    "ticker": "AAPL",
    "recommendation": "BUY|SELL|HOLD", 
    "sentiment_score": 0.65,
    "confidence": 0.82,
    "summary": "Based on multi-agent analysis..."
}
```

## Testing

Run the unit tests:

```bash
pytest tests/test_multiagent.py -v
```

## Future Enhancements

- Real market data integration
- Advanced ML models for sentiment analysis
- Risk management features
- Portfolio optimization
- Real-time streaming analysis

## Dependencies

- `langgraph>=0.2.0` - Multi-agent orchestration
- `langchain-core>=0.3.0` - Core LangChain components

## Note

This is a minimal implementation for demonstration purposes. In a production environment, you would integrate with real market data APIs, news sources, and social media platforms.