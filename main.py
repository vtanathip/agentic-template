"""Example usage of the LangGraph agent."""

from src.agentic_template import create_agent, AgentState


def main():
    """Run a simple example of the agent."""
    print("Creating LangGraph agent...")
    agent = create_agent()
    
    print("\nRunning agent with a test message...")
    initial_state: AgentState = {
        "messages": ["Hello, agent!"],
        "counter": 0
    }
    
    result = agent.invoke(initial_state)
    
    print(f"\nAgent processed {result['counter']} message(s)")
    print(f"Messages: {result['messages']}")
    print("\nAgent execution completed successfully!")


if __name__ == "__main__":
    main()

