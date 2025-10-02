"""FastAPI server for interacting with the LangGraph agent."""

from agentic_template.agent import create_agent, AgentState
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sys
import os
import time
import uuid

# Add src to Python path to import agent
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


class ChatMessage(BaseModel):
    """Request model for chat messages."""
    message: str


class ChatResponse(BaseModel):
    """Response model for chat responses."""
    response: str
    counter: int


# OpenAI-compatible models
class OpenAIMessage(BaseModel):
    """OpenAI-compatible message format."""
    role: str
    content: str


class OpenAIChatRequest(BaseModel):
    """OpenAI-compatible chat completion request."""
    model: str = "agentic-template"
    messages: List[OpenAIMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False


class OpenAIChatResponse(BaseModel):
    """OpenAI-compatible chat completion response."""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]


class OpenAIModelsResponse(BaseModel):
    """OpenAI-compatible models list response."""
    object: str = "list"
    data: List[Dict[str, Any]]


# Initialize FastAPI app
app = FastAPI(
    title="Agentic Template API",
    version="0.1.0",
    description="OpenAI-compatible API for LangGraph Agent",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize the agent
agent = create_agent()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Agentic Template API is running"}


@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage) -> ChatResponse:
    """
    Chat with the agent.

    Args:
        message: The message to send to the agent

    Returns:
        The agent's response and current counter value
    """
    try:
        # Create initial state with the message
        initial_state: AgentState = {
            "messages": [message.message],
            "counter": 0
        }

        # Run the agent
        result = agent.invoke(initial_state)

        # Extract response from messages
        response_messages = result.get("messages", [])
        if response_messages:
            last_message = response_messages[-1]
            # Handle both string and message objects
            if hasattr(last_message, 'content'):
                response_text = last_message.content
            else:
                response_text = str(last_message)
        else:
            response_text = "No response"
        counter = result.get("counter", 0)

        return ChatResponse(response=response_text, counter=counter)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing message: {str(e)}")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "agent": "ready"}


@app.get("/v1")
async def api_info():
    """OpenAI API info endpoint."""
    return {
        "object": "api",
        "version": "v1",
        "provider": "agentic-template",
        "models": ["agentic-template"]
    }


# OpenAI-compatible endpoints
@app.get("/v1/models")
async def list_models() -> OpenAIModelsResponse:
    """List available models (OpenAI-compatible)."""
    return OpenAIModelsResponse(
        data=[
            {
                "id": "agentic-template",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "agentic-template",
                "permission": [],
                "root": "agentic-template",
                "parent": None,
            }
        ]
    )


@app.post("/v1/chat/completions")
async def chat_completions(request: OpenAIChatRequest) -> OpenAIChatResponse:
    """
    OpenAI-compatible chat completions endpoint.

    This allows OpenWebUI to communicate with our agent using the standard OpenAI API format.
    """
    # Extract the last user message
    user_messages = [msg for msg in request.messages if msg.role == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="No user message found")

    try:

        last_user_message = user_messages[-1].content

        # Create initial state with the message
        initial_state: AgentState = {
            "messages": [last_user_message],
            "counter": 0
        }

        # Run the agent
        result = agent.invoke(initial_state)

        # Extract response from messages
        response_messages = result.get("messages", [])
        if response_messages:
            last_message = response_messages[-1]
            # Handle both string and message objects
            if hasattr(last_message, 'content'):
                response_text = last_message.content
            else:
                response_text = str(last_message)
        else:
            response_text = "No response"

        # Create OpenAI-compatible response
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:28]}"

        return OpenAIChatResponse(
            id=completion_id,
            created=int(time.time()),
            model=request.model,
            choices=[
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }
            ],
            usage={
                "prompt_tokens": len(last_user_message.split()),
                "completion_tokens": len(response_text.split()),
                "total_tokens": len(last_user_message.split()) + len(response_text.split())
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing chat completion: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
