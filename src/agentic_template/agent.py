"""Simple LangGraph agent implementation."""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State for the agent."""
    messages: Annotated[list, add_messages]
    counter: int


def process_message(state: AgentState) -> AgentState:
    """Process incoming message and increment counter."""
    messages = state["messages"]
    counter = state.get("counter", 0)
    
    # Simple processing: echo the message back
    if messages:
        last_message = messages[-1]
        response = f"Processed: {last_message}"
        return {
            "messages": [response],
            "counter": counter + 1
        }
    
    return state


def should_continue(state: AgentState) -> str:
    """Decide whether to continue processing."""
    counter = state.get("counter", 0)
    if counter >= 5:
        return "end"
    return "continue"


def create_agent():
    """Create and compile a simple LangGraph agent.
    
    Returns:
        A compiled LangGraph agent that processes messages and maintains a counter.
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("process", process_message)
    
    # Add edges
    workflow.set_entry_point("process")
    workflow.add_conditional_edges(
        "process",
        should_continue,
        {
            "continue": "process",
            "end": END
        }
    )
    
    # Compile the graph
    app = workflow.compile()
    return app
