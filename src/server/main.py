"""FastAPI server for interacting with the LangGraph agent."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Add src to Python path to import agent
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from agentic_template.agent import create_agent, AgentState


class ChatMessage(BaseModel):
    """Request model for chat messages."""
    message: str


class ChatResponse(BaseModel):
    """Response model for chat responses."""
    response: str
    counter: int


# Initialize FastAPI app
app = FastAPI(title="Agentic Template API", version="0.1.0")

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
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "agent": "ready"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)