"""
LangGraph RAG Agent with upload and query capabilities.
"""

from rag_template.retriever import DocumentRetriever
import os
from typing import Dict, Any, List, Optional, BinaryIO
from dataclasses import dataclass

try:
    from langgraph.graph import StateGraph, END
    from langchain_core.messages import HumanMessage, AIMessage
    import ollama
except ImportError:
    StateGraph = None
    END = None
    HumanMessage = None
    AIMessage = None
    ollama = None

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


@dataclass
class RAGState:
    """State for the RAG agent."""
    query: str = ""
    documents: List[Dict[str, Any]] = None
    response: str = ""
    action: str = ""  # "upload" or "query"
    file_content: Optional[BinaryIO] = None
    filename: str = ""
    error: Optional[str] = None

    def __post_init__(self):
        if self.documents is None:
            self.documents = []


class RAGAgent:
    """LangGraph-based RAG agent for document upload and querying."""

    def __init__(
        self,
        milvus_host: str | None = None,
        milvus_port: int | None = None,
        embedding_model: str | None = None,
        ollama_base_url: str | None = None,
        ollama_model: str = "llama3.2"
    ):
        """Initialize the RAG agent.

        Args:
            milvus_host: Milvus server host.
            milvus_port: Milvus server port.
            embedding_model: Name of the embedding model.
            ollama_base_url: Ollama server URL.
            ollama_model: Name of the Ollama model to use.
        """
        if StateGraph is None:
            raise ImportError("langgraph package is required")
        if ollama is None:
            raise ImportError("ollama package is required")

        self.retriever = DocumentRetriever(
            milvus_host=milvus_host,
            milvus_port=milvus_port,
            embedding_model=embedding_model
        )

        self.ollama_base_url = ollama_base_url or os.getenv(
            "OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = ollama_model

        # Configure ollama client
        if ollama:
            ollama_client = ollama.Client(host=self.ollama_base_url)
            self.ollama_client = ollama_client

        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        if StateGraph is None or END is None:
            raise ImportError("langgraph package is required")

        # Create state graph
        workflow = StateGraph(RAGState)

        # Add nodes
        workflow.add_node("router", self._route_action)
        workflow.add_node("upload_document", self._upload_document)
        workflow.add_node("query_documents", self._query_documents)
        workflow.add_node("generate_response", self._generate_response)

        # Add edges
        workflow.set_entry_point("router")

        # Conditional routing from router
        workflow.add_conditional_edges(
            "router",
            self._should_upload_or_query,
            {
                "upload": "upload_document",
                "query": "query_documents",
                "error": END
            }
        )

        # Both upload and query lead to response generation
        workflow.add_edge("upload_document", "generate_response")
        workflow.add_edge("query_documents", "generate_response")
        workflow.add_edge("generate_response", END)

        return workflow.compile()

    def _route_action(self, state: RAGState) -> RAGState:
        """Route the action based on the input."""
        # Action is determined by what's provided
        if state.file_content and state.filename:
            state.action = "upload"
        elif state.query:
            state.action = "query"
        else:
            state.error = "No valid action provided. Need either file upload or query."

        return state

    def _should_upload_or_query(self, state: RAGState) -> str:
        """Conditional edge function."""
        if state.error:
            return "error"
        return state.action

    def _upload_document(self, state: RAGState) -> RAGState:
        """Upload and process a document."""
        try:
            result = self.retriever.upload_document(
                state.file_content, state.filename)

            if result["success"]:
                state.response = (
                    f"Successfully uploaded {result['filename']}. "
                    f"Processed {result['chunks_processed']} chunks "
                    f"with {result['total_characters']} total characters."
                )
            else:
                state.error = result["message"]

        except Exception as e:
            state.error = f"Error uploading document: {str(e)}"

        return state

    def _query_documents(self, state: RAGState) -> RAGState:
        """Query documents for relevant information."""
        try:
            # Search for relevant documents
            results = self.retriever.search_documents(state.query, top_k=5)

            if results and not results[0].get("error"):
                state.documents = results
            else:
                state.error = results[0].get(
                    "error", "No relevant documents found")

        except Exception as e:
            state.error = f"Error querying documents: {str(e)}"

        return state

    def _generate_response(self, state: RAGState) -> RAGState:
        """Generate response using Ollama."""
        if state.error:
            state.response = f"Error: {state.error}"
            return state

        try:
            if state.action == "upload":
                # Response already set in upload_document
                return state

            elif state.action == "query":
                # Build context from retrieved documents
                context = ""
                if state.documents:
                    context_parts = []
                    # Use top 3 results and combine them as sections of the same document
                    for i, doc in enumerate(state.documents[:3]):
                        # Don't truncate, use full text for better context
                        context_parts.append(f"Section {i+1}:\n{doc['text']}")
                    context = "\n\n".join(context_parts)

                # Create prompt with better instructions
                prompt = f"""You are a helpful assistant that answers questions based on the provided document context.

IMPORTANT INSTRUCTIONS:
- The context below contains sections from the SAME document (it may have been split for processing)
- Always refer to it as "the document" or "the uploaded document", NOT as multiple documents
- Do not mention "Document 1, 2, 3" or section numbers in your response
- Synthesize information across all sections naturally
- If you cannot find relevant information, say so clearly without mentioning the internal structure

Context from the uploaded document:
{context}

User Question: {state.query}

Answer:"""

                # Generate response using Ollama
                if self.ollama_client:
                    response = self.ollama_client.generate(
                        model=self.ollama_model,
                        prompt=prompt
                    )
                    state.response = response["response"]
                else:
                    state.response = "Ollama client not available"

        except Exception as e:
            state.error = f"Error generating response: {str(e)}"
            state.response = f"Error: {state.error}"

        return state

    def upload_document(self, file_content: BinaryIO, filename: str) -> Dict[str, Any]:
        """Upload a document for indexing.

        Args:
            file_content: Binary file content.
            filename: Name of the file.

        Returns:
            Dictionary with upload results.
        """
        # Reset file pointer
        file_content.seek(0)

        initial_state = RAGState(
            file_content=file_content,
            filename=filename
        )

        result = self.graph.invoke(initial_state)

        return {
            "success": not bool(result.get("error")),
            "message": result.get("response") or result.get("error", "Unknown error"),
            "filename": filename
        }

    def query(self, query: str) -> str:
        """Query the knowledge base.

        Args:
            query: The question to ask.

        Returns:
            Generated response.
        """
        initial_state = RAGState(query=query)
        result = self.graph.invoke(initial_state)
        return result.get("response", "No response generated")
    
    def query_stream(self, query: str):
        """Query the knowledge base with streaming response.
        
        Args:
            query: The question to ask.
            
        Yields:
            String chunks as they're generated by the LLM.
        """
        try:
            # Retrieve relevant documents
            results = self.retriever.search_documents(query, top_k=5)
            
            if not results or results[0].get("error"):
                yield "I don't have any information about that in my knowledge base."
                return
            
            # Build context from retrieved documents
            context_parts = []
            for i, doc in enumerate(results[:3]):
                context_parts.append(f"Section {i+1}:\n{doc['text']}")
            context = "\n\n".join(context_parts)
            
            # Create prompt with better instructions
            prompt = f"""You are a helpful assistant that answers questions based on the provided document context.

IMPORTANT INSTRUCTIONS:
- The context below contains sections from the SAME document (it may have been split for processing)
- Always refer to it as "the document" or "the uploaded document", NOT as multiple documents
- Do not mention "Document 1, 2, 3" or section numbers in your response
- Synthesize information across all sections naturally
- If you cannot find relevant information, say so clearly without mentioning the internal structure

Context from the uploaded document:
{context}

User Question: {query}

Answer:"""
            
            # Stream from Ollama
            if self.ollama_client:
                stream = self.ollama_client.generate(
                    model=self.ollama_model,
                    prompt=prompt,
                    stream=True  # Enable streaming!
                )
                
                # Yield each token as it's generated
                for chunk in stream:
                    if chunk.get('response'):
                        yield chunk['response']
            else:
                yield "Ollama client not available"
                
        except Exception as e:
            yield f"Error: {str(e)}"

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        return self.retriever.get_stats()

    def delete_document(self, filename: str) -> Dict[str, Any]:
        """Delete a document from the knowledge base."""
        return self.retriever.delete_document(filename)


def create_rag_agent(config=None):
    """Factory function to create RAG agent for LangGraph Studio.

    Args:
        config: Configuration object (required by LangGraph but can be ignored)

    Returns:
        Compiled LangGraph workflow
    """
    agent = RAGAgent()
    return agent.graph
