"""FastAPI server for multi-agent trading system."""

from src.multiagent_template import TradingSystem
import json
import asyncio
import sys
from pathlib import Path
from typing import AsyncGenerator, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
import logging

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Multi-Agent Trading System API",
    description="FastAPI server for streaming multi-agent stock analysis",
    version="1.0.0"
)


class AnalysisRequest(BaseModel):
    """Request model for stock analysis."""
    ticker: str = Field(..., description="Stock ticker symbol to analyze")
    stream: bool = Field(
        default=True, description="Whether to stream the response")


class AnalysisResponse(BaseModel):
    """Response model for stock analysis."""
    ticker: str
    recommendation: str
    sentiment_score: float
    confidence: float
    summary: str
    details: Dict[str, Any] = Field(default_factory=dict)


class StreamEvent(BaseModel):
    """Event model for streaming responses."""
    event: str
    data: Dict[str, Any]


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "multiagent-api"}


@app.post("/analyze")
async def analyze_stock(request: AnalysisRequest):
    """Analyze a stock using the multi-agent system."""
    try:
        if request.stream:
            return StreamingResponse(
                stream_analysis(request.ticker),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                }
            )
        else:
            # Non-streaming response
            trading_system = TradingSystem()
            result = trading_system.analyze_stock(request.ticker)
            return AnalysisResponse(**result)

    except Exception as e:
        logger.error(f"Error analyzing {request.ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def stream_analysis(ticker: str) -> AsyncGenerator[str, None]:
    """Stream the analysis process for a stock ticker."""
    try:
        trading_system = TradingSystem()

        # Send initial event
        initial_event = StreamEvent(
            event="analysis_started",
            data={"ticker": ticker, "message": f"Starting analysis for {ticker}"}
        )
        yield f"data: {initial_event.model_dump_json()}\n\n"

        # Create initial state
        from src.multiagent_template.trading_system import TradingState
        initial_state: TradingState = {
            "ticker": ticker,
            "messages": [HumanMessage(content=f"Analyze {ticker}")],
            "news_analysis": {},
            "social_analysis": {},
            "technical_analysis": {},
            "final_recommendation": {}
        }

        # Stream through the graph execution
        step_count = 0
        async for state in trading_system.graph.astream(initial_state):
            step_count += 1

            # Extract the current node being executed
            node_name = list(state.keys())[0] if state else "unknown"
            state_data = list(state.values())[0] if state else {}

            # Create progress event
            progress_event = StreamEvent(
                event="analysis_progress",
                data={
                    "ticker": ticker,
                    "step": step_count,
                    "current_node": node_name,
                    "message": f"Executing {node_name}..."
                }
            )
            yield f"data: {progress_event.model_dump_json()}\n\n"

            # Send specific analysis results when available
            if "news_analysis" in state_data and state_data["news_analysis"]:
                news_event = StreamEvent(
                    event="news_analysis_complete",
                    data={
                        "ticker": ticker,
                        "analysis": state_data["news_analysis"]
                    }
                )
                yield f"data: {news_event.model_dump_json()}\n\n"

            if "social_analysis" in state_data and state_data["social_analysis"]:
                social_event = StreamEvent(
                    event="social_analysis_complete",
                    data={
                        "ticker": ticker,
                        "analysis": state_data["social_analysis"]
                    }
                )
                yield f"data: {social_event.model_dump_json()}\n\n"

            if "technical_analysis" in state_data and state_data["technical_analysis"]:
                technical_event = StreamEvent(
                    event="technical_analysis_complete",
                    data={
                        "ticker": ticker,
                        "analysis": state_data["technical_analysis"]
                    }
                )
                yield f"data: {technical_event.model_dump_json()}\n\n"

            if "final_recommendation" in state_data and state_data["final_recommendation"]:
                # Final result event
                final_event = StreamEvent(
                    event="analysis_complete",
                    data={
                        "ticker": ticker,
                        "result": state_data["final_recommendation"]
                    }
                )
                yield f"data: {final_event.model_dump_json()}\n\n"
                break

            # Add small delay to make streaming visible
            await asyncio.sleep(0.1)

        # Send completion event
        completion_event = StreamEvent(
            event="stream_complete",
            data={"ticker": ticker, "message": "Analysis stream completed"}
        )
        yield f"data: {completion_event.model_dump_json()}\n\n"

    except Exception as e:
        logger.error(f"Error in stream analysis for {ticker}: {e}")
        error_event = StreamEvent(
            event="error",
            data={"ticker": ticker, "error": str(e)}
        )
        yield f"data: {error_event.model_dump_json()}\n\n"


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Multi-Agent Trading System API",
        "version": "1.0.0",
        "endpoints": {
            "/health": "Health check",
            "/analyze": "Analyze stock (POST)",
            "/docs": "API documentation"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
