"""Unit tests for the LangGraph agent."""

import pytest
from src.agentic_template.agent import (
    create_agent,
    AgentState,
    process_message,
    should_continue
)


def test_process_message():
    """Test the process_message function."""
    state: AgentState = {
        "messages": ["Hello"],
        "counter": 0
    }
    
    result = process_message(state)
    
    assert result["counter"] == 1
    assert len(result["messages"]) == 1
    assert "Processed: Hello" in result["messages"][0]


def test_process_message_empty():
    """Test process_message with empty messages."""
    state: AgentState = {
        "messages": [],
        "counter": 0
    }
    
    result = process_message(state)
    
    assert result == state


def test_should_continue_below_threshold():
    """Test should_continue when counter is below threshold."""
    state: AgentState = {
        "messages": [],
        "counter": 3
    }
    
    result = should_continue(state)
    
    assert result == "continue"


def test_should_continue_at_threshold():
    """Test should_continue when counter reaches threshold."""
    state: AgentState = {
        "messages": [],
        "counter": 5
    }
    
    result = should_continue(state)
    
    assert result == "end"


def test_should_continue_above_threshold():
    """Test should_continue when counter exceeds threshold."""
    state: AgentState = {
        "messages": [],
        "counter": 10
    }
    
    result = should_continue(state)
    
    assert result == "end"


def test_create_agent():
    """Test agent creation."""
    agent = create_agent()
    
    # Verify the agent can be invoked
    assert agent is not None
    
    # Test a simple invocation
    initial_state: AgentState = {
        "messages": ["Test message"],
        "counter": 0
    }
    
    result = agent.invoke(initial_state)
    
    assert "messages" in result
    assert "counter" in result
    assert result["counter"] > 0


def test_agent_execution():
    """Test full agent execution."""
    agent = create_agent()
    
    initial_state: AgentState = {
        "messages": ["Start"],
        "counter": 0
    }
    
    result = agent.invoke(initial_state)
    
    # Verify the agent processed messages
    assert result["counter"] >= 1
    assert len(result["messages"]) >= 1
