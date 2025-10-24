"""
Example usage of the OpenWebUI Pipeline programmatically.
This demonstrates how the pipeline would be called by OpenWebUI.
"""

from openwebui.langgraph_pipeline import Pipeline
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def example_agentic_chat():
    """Example: Chat with the Agentic Template."""
    print("\n" + "="*60)
    print("Example 1: Agentic Template Chat")
    print("="*60)

    pipeline = Pipeline()

    messages = [
        {"role": "user", "content": "Hello, how are you?"}
    ]
    body = {"stream": False}

    response = pipeline.pipe("Hello, how are you?", "model-id", messages, body)

    print(f"\nUser: Hello, how are you?")
    print(f"Assistant: {response}")


def example_streaming_chat():
    """Example: Streaming chat with the Agentic Template."""
    print("\n" + "="*60)
    print("Example 2: Streaming Response")
    print("="*60)

    pipeline = Pipeline()

    messages = [
        {"role": "user", "content": "Tell me a story"}
    ]
    body = {"stream": True}

    response = pipeline.pipe("Tell me a story", "model-id", messages, body)

    print(f"\nUser: Tell me a story")
    print(f"Assistant (streaming): ", end="")

    try:
        for chunk in response:
            if chunk:
                print(".", end="", flush=True)
    except Exception as e:
        print(f"\nNote: Streaming complete or error: {e}")

    print()


def example_rag_query():
    """Example: Query documents using RAG mode."""
    print("\n" + "="*60)
    print("Example 3: RAG Document Query")
    print("="*60)

    pipeline = Pipeline()
    pipeline.valves.USE_RAG = True  # Enable RAG mode

    messages = [
        {"role": "user", "content": "What documents are available?"}
    ]
    body = {}

    response = pipeline.pipe(
        "What documents are available?", "model-id", messages, body)

    print(f"\nUser: What documents are available?")
    print(f"Assistant (RAG): {response}")


def example_multi_turn_conversation():
    """Example: Multi-turn conversation."""
    print("\n" + "="*60)
    print("Example 4: Multi-turn Conversation")
    print("="*60)

    pipeline = Pipeline()

    # First message
    messages = [
        {"role": "user", "content": "Hello"}
    ]

    response1 = pipeline.pipe("Hello", "model-id", messages, {"stream": False})
    print(f"\nUser: Hello")
    print(f"Assistant: {response1}")

    # Second message (includes conversation history)
    messages.append({"role": "assistant", "content": response1})
    messages.append({"role": "user", "content": "How are you?"})

    response2 = pipeline.pipe(
        "How are you?", "model-id", messages, {"stream": False})
    print(f"\nUser: How are you?")
    print(f"Assistant: {response2}")


def example_custom_configuration():
    """Example: Custom pipeline configuration."""
    print("\n" + "="*60)
    print("Example 5: Custom Configuration")
    print("="*60)

    pipeline = Pipeline()

    # Customize configuration
    pipeline.valves.AGENTIC_API_URL = "http://custom-host:9000"
    pipeline.valves.TIMEOUT = 60

    print(f"\nCustom Configuration:")
    print(f"  Agentic API URL: {pipeline.valves.AGENTIC_API_URL}")
    print(f"  RAG API URL: {pipeline.valves.RAG_API_URL}")
    print(f"  Use RAG: {pipeline.valves.USE_RAG}")
    print(f"  Timeout: {pipeline.valves.TIMEOUT}s")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("OpenWebUI Pipeline Examples")
    print("="*60)
    print("\nNote: These examples require the APIs to be running:")
    print("  - Agentic API: http://localhost:8000")
    print("  - RAG API: http://localhost:8001")

    try:
        example_agentic_chat()
        example_streaming_chat()
        example_rag_query()
        example_multi_turn_conversation()
        example_custom_configuration()

        print("\n" + "="*60)
        print("✓ All examples completed!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        print("\nMake sure your APIs are running:")
        print("  uv run uvicorn src.server.main:app --port 8000")
        print("  cd docker && docker-compose up -d")


if __name__ == "__main__":
    main()
