"""Example usage of the Multi-Agent Trading System API."""

import asyncio
import json
import httpx
from typing import AsyncIterator


async def test_streaming_analysis(ticker: str = "AAPL"):
    """Test the streaming analysis endpoint."""
    print(f"🤖 Testing streaming analysis for {ticker}")
    print("=" * 50)

    url = "http://localhost:8000/analyze"
    payload = {"ticker": ticker, "stream": True}

    try:
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                url,
                json=payload,
                headers={"Accept": "text/event-stream"}
            ) as response:
                print(f"Response status: {response.status_code}")

                if response.status_code == 200:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            try:
                                event_data = json.loads(line[6:])
                                event_type = event_data.get("event", "unknown")
                                data = event_data.get("data", {})

                                print(f"📊 {event_type}: {data}")

                                # Break when analysis is complete
                                if event_type == "stream_complete":
                                    break

                            except json.JSONDecodeError:
                                print(f"Failed to parse: {line}")
                else:
                    print(f"Error: {response.status_code}")
                    print(await response.aread())

    except httpx.ConnectError:
        print("❌ Could not connect to server. Make sure the server is running:")
        print("   uv run python -m src.server.multiagent_api.main")
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_non_streaming_analysis(ticker: str = "TSLA"):
    """Test the non-streaming analysis endpoint."""
    print(f"\n🤖 Testing non-streaming analysis for {ticker}")
    print("=" * 50)

    url = "http://localhost:8000/analyze"
    payload = {"ticker": ticker, "stream": False}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)

            print(f"Response status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"📈 Analysis Result:")
                print(f"   Ticker: {result['ticker']}")
                print(f"   Recommendation: {result['recommendation']}")
                print(f"   Sentiment Score: {result['sentiment_score']}")
                print(f"   Confidence: {result['confidence']:.0%}")
                print(f"   Summary: {result['summary']}")
            else:
                print(f"Error: {response.status_code}")
                print(response.text)

    except httpx.ConnectError:
        print("❌ Could not connect to server. Make sure the server is running:")
        print("   uv run python -m src.server.multiagent_api.main")
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_health_check():
    """Test the health check endpoint."""
    print("\n🏥 Testing health check")
    print("=" * 50)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")

            print(f"Response status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Health Status: {result['status']}")
                print(f"   Service: {result['service']}")
            else:
                print(f"Error: {response.status_code}")

    except httpx.ConnectError:
        print("❌ Could not connect to server. Make sure the server is running:")
        print("   uv run python -m src.server.multiagent_api.main")
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run all tests."""
    print("🚀 Multi-Agent Trading System API Test Suite")
    print("=" * 60)

    await test_health_check()
    await test_non_streaming_analysis("TSLA")
    await test_streaming_analysis("AAPL")

    print("\n✅ Test suite completed!")
    print("\nTo start the server, run:")
    print("   uv run python -m src.server.multiagent_api.main")


if __name__ == "__main__":
    asyncio.run(main())
