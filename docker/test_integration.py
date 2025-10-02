#!/usr/bin/env python3
"""
Test script to verify OpenWebUI integration with FastAPI backend.
"""

import requests
import json


def test_fastapi_health():
    """Test FastAPI health endpoint."""
    try:
        response = requests.get("http://localhost:8000/health")
        response.raise_for_status()
        print("✅ FastAPI health check: PASSED")
        return True
    except Exception as e:
        print(f"❌ FastAPI health check: FAILED - {e}")
        return False


def test_openai_models():
    """Test OpenAI-compatible models endpoint."""
    try:
        response = requests.get("http://localhost:8000/v1/models")
        response.raise_for_status()
        data = response.json()

        if data.get("object") == "list" and len(data.get("data", [])) > 0:
            print("✅ OpenAI models endpoint: PASSED")
            return True
        else:
            print("❌ OpenAI models endpoint: FAILED - Invalid response format")
            return False
    except Exception as e:
        print(f"❌ OpenAI models endpoint: FAILED - {e}")
        return False


def test_chat_completions():
    """Test OpenAI-compatible chat completions endpoint."""
    try:
        payload = {
            "model": "agentic-template",
            "messages": [
                {"role": "user", "content": "Hello, how are you?"}
            ]
        }

        response = requests.post(
            "http://localhost:8000/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        data = response.json()

        if (data.get("object") == "chat.completion" and
            len(data.get("choices", [])) > 0 and
                data["choices"][0].get("message", {}).get("role") == "assistant"):
            print("✅ Chat completions endpoint: PASSED")
            print(f"   Response: {data['choices'][0]['message']['content']}")
            return True
        else:
            print("❌ Chat completions endpoint: FAILED - Invalid response format")
            return False
    except Exception as e:
        print(f"❌ Chat completions endpoint: FAILED - {e}")
        return False


def test_openwebui():
    """Test OpenWebUI accessibility."""
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("✅ OpenWebUI accessibility: PASSED")
            return True
        else:
            print(
                f"❌ OpenWebUI accessibility: FAILED - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OpenWebUI accessibility: FAILED - {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing Agentic Template + OpenWebUI Integration")
    print("=" * 50)

    tests = [
        test_fastapi_health,
        test_openai_models,
        test_chat_completions,
        test_openwebui,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Your setup is working correctly.")
        print("\n🌐 Access points:")
        print("   • FastAPI API: http://localhost:8000")
        print("   • API Documentation: http://localhost:8000/docs")
        print("   • OpenWebUI Chat: http://localhost:3000")
    else:
        print("⚠️  Some tests failed. Please check the Docker containers and network connectivity.")

    return passed == total


if __name__ == "__main__":
    main()
