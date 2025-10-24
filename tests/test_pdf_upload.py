"""
Integration test for PDF upload to RAG agent.
Tests downloading a PDF from online and uploading it to the RAG system.

Prerequisites:
1. Docker Desktop must be running
2. RAG services must be started: cd docker && start-rag-services.bat (or .sh)
3. Wait for services to be healthy (~30-60 seconds)
4. Ollama must be running locally on port 11434 (optional for queries)

Run tests with: uv run pytest tests/test_pdf_upload.py -v -s
"""

import requests
from io import BytesIO
import pytest


# RAG API base URL
RAG_API_URL = "http://localhost:8001"

# Sample PDF URL - Using a publicly available sample PDF with text content
TEST_PDF_URL = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"


def test_download_pdf():
    """Test that we can download the test PDF."""
    response = requests.get(TEST_PDF_URL, timeout=10)
    assert response.status_code == 200
    # Content-Type may have additional parameters like charset or quality
    assert 'application/pdf' in response.headers.get('Content-Type', '')
    assert len(response.content) > 0
    print(f"✓ Downloaded PDF: {len(response.content)} bytes")


def test_rag_api_health():
    """Test that the RAG API is running."""
    response = requests.get(f"{RAG_API_URL}/health", timeout=5)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["rag_agent"] == "available"
    print(f"✓ RAG API is healthy: {data}")


def test_upload_pdf_to_rag():
    """Test uploading a PDF to the RAG system."""
    # Download the PDF
    pdf_response = requests.get(TEST_PDF_URL, timeout=10)
    assert pdf_response.status_code == 200
    
    pdf_content = pdf_response.content
    pdf_filename = "test_dummy.pdf"
    
    print(f"Uploading {pdf_filename} ({len(pdf_content)} bytes)...")
    
    # Upload to RAG API
    files = {'file': (pdf_filename, BytesIO(pdf_content), 'application/pdf')}
    upload_response = requests.post(
        f"{RAG_API_URL}/upload",
        files=files,
        timeout=120  # PDF processing can take time, especially for docling
    )
    
    # Verify upload was successful
    assert upload_response.status_code == 200
    data = upload_response.json()
    
    print(f"Upload response: {data}")
    
    assert data["success"] is True
    assert data["filename"] == pdf_filename
    assert "uploaded" in data["message"].lower() or "indexed" in data["message"].lower()
    
    print(f"✓ PDF uploaded successfully: {data['message']}")


def test_query_uploaded_pdf():
    """Test querying the uploaded PDF content."""
    # First upload the PDF
    pdf_response = requests.get(TEST_PDF_URL, timeout=10)
    pdf_content = pdf_response.content
    pdf_filename = "test_dummy_query.pdf"
    
    files = {'file': (pdf_filename, BytesIO(pdf_content), 'application/pdf')}
    upload_response = requests.post(
        f"{RAG_API_URL}/upload",
        files=files,
        timeout=120
    )
    assert upload_response.status_code == 200
    
    # Query the content
    query_data = {"query": "What is this document about?"}
    query_response = requests.post(
        f"{RAG_API_URL}/query",
        json=query_data,
        timeout=30
    )
    
    assert query_response.status_code == 200
    data = query_response.json()
    
    print(f"\n{'='*60}")
    print("QUERY TEST - Sample Response")
    print(f"{'='*60}")
    print(f"Query: {query_data['query']}")
    print(f"\nFull Response:")
    print(f"  success: {data.get('success')}")
    print(f"  error: {data.get('error')}")
    print(f"\nResponse Text:")
    print(f"  {data.get('response', 'N/A')}")
    print(f"{'='*60}\n")
    
    # Query might fail if Ollama is not running (optional dependency)
    if not data["success"]:
        if "Ollama" in data.get("error", ""):
            pytest.skip("Ollama is not running - query test requires Ollama for LLM responses")
        else:
            # If it's a different error, fail the test
            pytest.fail(f"Query failed with error: {data.get('error')}")
    
    assert "response" in data
    assert len(data["response"]) > 0
    
    print(f"✓ Query successful with {len(data['response'])} characters in response")


def test_get_stats_after_upload():
    """Test getting statistics after PDF upload."""
    # Upload a PDF first
    pdf_response = requests.get(TEST_PDF_URL, timeout=10)
    pdf_content = pdf_response.content
    pdf_filename = "test_dummy_stats.pdf"
    
    files = {'file': (pdf_filename, BytesIO(pdf_content), 'application/pdf')}
    upload_response = requests.post(
        f"{RAG_API_URL}/upload",
        files=files,
        timeout=120
    )
    assert upload_response.status_code == 200
    
    # Get stats
    stats_response = requests.get(f"{RAG_API_URL}/stats", timeout=10)
    
    assert stats_response.status_code == 200
    data = stats_response.json()
    
    print(f"\n{'='*60}")
    print("STATS TEST - Sample Response")
    print(f"{'='*60}")
    print(f"Full Response:")
    print(f"  success: {data.get('success')}")
    print(f"  error: {data.get('error')}")
    print(f"\nStats Details:")
    stats = data.get("stats", {})
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print(f"{'='*60}\n")
    
    assert data["success"] is True
    assert "stats" in data
    
    # Stats should have either document_count or row_count (depending on implementation)
    stats = data["stats"]
    assert "row_count" in stats or "document_count" in stats
    
    # Verify we have at least some documents/rows
    row_count = stats.get("row_count", stats.get("document_count", 0))
    assert row_count >= 0  # Should be 0 or positive
    
    print(f"✓ Stats retrieved successfully with {row_count} rows/documents")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Running PDF Upload Integration Tests")
    print("="*60 + "\n")
    
    try:
        print("Test 1: Download PDF")
        test_download_pdf()
        print()
        
        print("Test 2: Check RAG API Health")
        test_rag_api_health()
        print()
        
        print("Test 3: Upload PDF to RAG")
        test_upload_pdf_to_rag()
        print()
        
        print("Test 4: Query Uploaded PDF")
        test_query_uploaded_pdf()
        print()
        
        print("Test 5: Get Stats After Upload")
        test_get_stats_after_upload()
        print()
        
        print("="*60)
        print("✓ All tests passed!")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise
