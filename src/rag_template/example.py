"""
Simple usage example for the RAG template.
"""

import io
from rag_template.rag_agent import RAGAgent


def main():
    """Demonstrate basic RAG functionality."""
    print("RAG Template Usage Example")
    print("=" * 30)

    try:
        # Initialize the RAG agent
        print("Initializing RAG agent...")
        agent = RAGAgent(
            milvus_host="localhost",
            milvus_port=19530,
            embedding_model="all-MiniLM-L6-v2",
            ollama_model="llama3.2"
        )

        # Create a sample document
        sample_doc = """
        The History of Artificial Intelligence
        
        Artificial Intelligence (AI) has a rich history dating back to the 1950s.
        The term was coined by John McCarthy in 1956 at the Dartmouth Conference.
        
        Early AI research focused on symbolic reasoning and expert systems.
        In the 1980s, machine learning gained prominence with the development
        of neural networks and statistical methods.
        
        The 1990s saw the rise of more practical AI applications in areas
        like speech recognition and computer vision.
        
        The 2000s brought about significant advances in deep learning,
        leading to breakthroughs in image recognition and natural language processing.
        
        Today, AI is integrated into many aspects of our daily lives,
        from search engines to recommendation systems to autonomous vehicles.
        """

        # Upload the document
        print("\nUploading sample document...")
        file_content = io.BytesIO(sample_doc.encode('utf-8'))
        upload_result = agent.upload_document(file_content, "ai_history.txt")

        if upload_result["success"]:
            print(f"✓ Document uploaded successfully!")
            print(
                f"  Chunks processed: {upload_result.get('chunks_processed', 'N/A')}")
        else:
            print(f"✗ Upload failed: {upload_result['message']}")
            return

        # Wait a moment for indexing
        import time
        print("Waiting for indexing...")
        time.sleep(2)

        # Test queries
        queries = [
            "When was the term 'Artificial Intelligence' coined?",
            "What happened in AI research during the 1980s?",
            "How is AI used today?",
            "Who is John McCarthy?"
        ]

        print("\nTesting queries:")
        print("-" * 20)

        for query in queries:
            print(f"\nQ: {query}")
            try:
                response = agent.query(query)
                print(f"A: {response}")
            except Exception as e:
                print(f"Error: {str(e)}")

        # Get statistics
        print("\nKnowledge base statistics:")
        try:
            stats = agent.get_stats()
            if "error" not in stats:
                print(f"Total documents: {stats.get('row_count', 0)}")
            else:
                print(f"Error getting stats: {stats['error']}")
        except Exception as e:
            print(f"Error getting stats: {str(e)}")

        print("\nExample completed successfully!")

    except ImportError as e:
        print(f"Missing dependencies: {e}")
        print("Please install dependencies with: uv sync")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Make sure Milvus and Ollama are running.")


if __name__ == "__main__":
    main()
