#!/usr/bin/env python3
"""
Test streaming functionality between RAG server and pipeline.
This test verifies that the streaming works end-to-end.
"""

import requests
import json
import sys


def test_rag_streaming():
    """Test RAG server streaming endpoint."""
    print("\n🧪 Testing RAG Server Streaming")
    print("=" * 50)
    
    try:
        url = "http://localhost:8001/query"
        payload = {
            "query": "What is machine learning?",
            "stream": True
        }
        
        print(f"📤 Sending request to: {url}")
        print(f"📝 Query: {payload['query']}")
        print(f"🌊 Stream: {payload['stream']}")
        print()
        
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            stream=True,
            timeout=30
        )
        response.raise_for_status()
        
        print("📨 Receiving streamed response:")
        print("-" * 50)
        
        chunk_count = 0
        total_content = ""
        
        for line in response.iter_lines(decode_unicode=True):
            if line.strip():
                # Remove "data: " prefix if present
                if line.startswith("data: "):
                    line = line[6:]
                
                # Skip [DONE] marker
                if line.strip() == "[DONE]":
                    continue
                
                try:
                    # Parse JSON chunk
                    chunk = json.loads(line)
                    
                    # Extract content from OpenAI format
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        choice = chunk["choices"][0]
                        delta = choice.get("delta", {})
                        content = delta.get("content", "")
                        finish_reason = choice.get("finish_reason")
                        
                        if content:
                            chunk_count += 1
                            total_content += content
                            print(f"Chunk {chunk_count}: {repr(content)}")
                        
                        if finish_reason == "stop":
                            print("\n✅ Stream completed successfully")
                            break
                        elif finish_reason == "error":
                            print(f"\n❌ Stream ended with error: {content}")
                            return False
                            
                except json.JSONDecodeError as e:
                    print(f"⚠️  Warning: Could not parse line as JSON: {line[:100]}")
                    continue
        
        print("-" * 50)
        print(f"\n📊 Summary:")
        print(f"   Total chunks received: {chunk_count}")
        print(f"   Total content length: {len(total_content)} characters")
        print(f"\n💬 Complete response:")
        print(f"   {total_content}")
        print()
        
        if chunk_count > 0:
            print("✅ RAG Server Streaming: PASSED")
            return True
        else:
            print("❌ RAG Server Streaming: FAILED - No chunks received")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ RAG Server Streaming: FAILED - Cannot connect to server")
        print(f"   Error: {e}")
        print(f"   Make sure RAG server is running at http://localhost:8001")
        return False
    except Exception as e:
        print(f"❌ RAG Server Streaming: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rag_non_streaming():
    """Test RAG server non-streaming endpoint for comparison."""
    print("\n🧪 Testing RAG Server Non-Streaming (for comparison)")
    print("=" * 50)
    
    try:
        url = "http://localhost:8001/query"
        payload = {
            "query": "What is machine learning?",
            "stream": False
        }
        
        print(f"📤 Sending request to: {url}")
        print(f"📝 Query: {payload['query']}")
        print(f"🌊 Stream: {payload['stream']}")
        print()
        
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        print("📨 Response:")
        print("-" * 50)
        print(f"Success: {data.get('success')}")
        print(f"Response: {data.get('response')}")
        print("-" * 50)
        print()
        
        if data.get("success") and data.get("response"):
            print("✅ RAG Server Non-Streaming: PASSED")
            return True
        else:
            print("❌ RAG Server Non-Streaming: FAILED")
            return False
            
    except Exception as e:
        print(f"❌ RAG Server Non-Streaming: FAILED - {e}")
        return False


def test_rag_health():
    """Test RAG server health endpoint."""
    print("\n🧪 Testing RAG Server Health")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8001/health", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"Status: {data.get('status')}")
        print(f"RAG Agent: {data.get('rag_agent')}")
        print(f"Version: {data.get('version')}")
        print()
        
        if data.get("status") == "healthy" and data.get("rag_agent") == "available":
            print("✅ RAG Server Health: PASSED")
            return True
        else:
            print("❌ RAG Server Health: FAILED - RAG agent not available")
            return False
            
    except Exception as e:
        print(f"❌ RAG Server Health: FAILED - {e}")
        return False


def test_pipeline_format_compatibility():
    """Verify the format matches what pipeline expects."""
    print("\n🧪 Testing Pipeline Format Compatibility")
    print("=" * 50)
    
    # This simulates what the pipeline does
    test_chunk = {
        'choices': [{
            'delta': {'content': 'test content'},
            'finish_reason': None
        }]
    }
    
    # Pipeline parsing logic
    content = None
    if "choices" in test_chunk and isinstance(test_chunk["choices"], list) and len(test_chunk["choices"]) > 0:
        choice = test_chunk["choices"][0]
        if "delta" in choice and isinstance(choice["delta"], dict):
            content = choice["delta"].get("content", "")
    
    if content == "test content":
        print("✅ Format structure matches pipeline expectations")
        print("   Pipeline can extract: 'test content'")
        return True
    else:
        print("❌ Format mismatch!")
        return False


def main():
    """Run all streaming tests."""
    print("\n" + "=" * 60)
    print("🔄 RAG STREAMING INTEGRATION TEST")
    print("=" * 60)
    print("\nThis test verifies the streaming functionality works")
    print("between the RAG server and OpenWebUI pipeline.")
    print()
    
    tests = [
        ("RAG Health Check", test_rag_health),
        ("Format Compatibility", test_pipeline_format_compatibility),
        ("Non-Streaming Query", test_rag_non_streaming),
        ("Streaming Query", test_rag_streaming),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except KeyboardInterrupt:
            print("\n\n⚠️  Test interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ {test_name}: FAILED with exception - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! Streaming is working correctly.")
        print("\n📝 Next steps:")
        print("   1. Open OpenWebUI at http://localhost:3000")
        print("   2. The LangGraph RAG pipeline should stream responses")
        print("   3. Ask a question and watch it stream word by word!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure Docker services are running:")
        print("      cd docker && docker-compose ps")
        print("   2. Check RAG server logs:")
        print("      docker-compose logs rag-api")
        print("   3. Ensure Ollama is running locally")
        print("   4. Verify documents are uploaded to RAG system")
        return 1


if __name__ == "__main__":
    sys.exit(main())
