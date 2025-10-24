"""
title: LangGraph Agentic RAG Pipeline
author: vtanathip
author_url: https://github.com/vtanathip
git_url: https://github.com/vtanathip/agentic-template
description: OpenWebUI Pipeline for LangGraph Agentic RAG with streaming support (synced with RAG server SSE format)
required_open_webui_version: 0.4.3
requirements: requests
version: 2.1.0
licence: MIT
"""

import json
import requests
from pydantic import BaseModel, Field
from typing import List, Union, Generator, Iterator, Optional, Any


class Pipeline:
    """OpenWebUI Pipeline for LangGraph Agentic RAG."""

    class Valves(BaseModel):
        """Configuration parameters for the pipeline."""
        RAG_API_URL: str = Field(
            default="http://rag-api:8001",
            description="Base URL for the Agentic RAG API"
        )
        TIMEOUT: int = Field(
            default=120,
            description="Request timeout in seconds"
        )

    def __init__(self):
        """Initialize the pipeline."""
        self.id = "langgraph_agentic_rag"
        self.name = "LangGraph Agentic RAG"

        # Initialize valve parameters
        self.valves = self.Valves()

    async def on_startup(self):
        """Called when the server starts."""
        print(f"on_startup: {__name__}")
        print(f"RAG API URL: {self.valves.RAG_API_URL}")

    async def on_shutdown(self):
        """Called when the server shuts down."""
        print(f"on_shutdown: {__name__}")

    async def on_valves_updated(self):
        """Called when valve parameters are updated."""
        print(f"on_valves_updated: RAG API URL: {self.valves.RAG_API_URL}")

    def pipe(
        self,
        user_message: str,
        model_id: str,
        messages: List[dict],
        body: dict
    ) -> Union[str, Generator, Iterator, Any]:
        """
        Process messages through the Agentic RAG system with streaming.

        Args:
            user_message: The latest user message
            model_id: Model identifier
            messages: List of conversation messages
            body: Request body containing additional parameters

        Returns:
            Response generator for streaming
        """
        try:
            return self._stream_rag_response(user_message, messages)

        except requests.exceptions.ConnectionError as e:
            error_msg = f"Failed to connect to RAG API. Please check that the server is running.\nError: {str(e)}"
            print(error_msg)
            return error_msg
        except requests.exceptions.Timeout as e:
            error_msg = f"Request timed out after {self.valves.TIMEOUT} seconds.\nError: {str(e)}"
            print(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error in RAG pipeline: {str(e)}"
            print(error_msg)
            return error_msg

    def _stream_rag_response(
        self,
        user_message: str,
        messages: List[dict]
    ) -> Generator[str, None, None]:
        """
        Stream RAG query results to the frontend.
        
        This method expects the RAG server to return SSE (Server-Sent Events) 
        in OpenAI-compatible format:
        {
            "choices": [{
                "delta": {"content": "text chunk"},
                "finish_reason": null | "stop" | "error"
            }]
        }

        Args:
            user_message: The user's question
            messages: Conversation history

        Yields:
            Text chunks as they are generated
        """
        # Prepare request data
        data = {
            "query": user_message,
            "stream": True
        }

        url = f"{self.valves.RAG_API_URL}/query"
        headers = {
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                url,
                json=data,
                headers=headers,
                stream=True,
                timeout=self.valves.TIMEOUT
            )
            response.raise_for_status()

            # Stream the response
            for line in response.iter_lines(decode_unicode=True):
                if line.strip():
                    # Skip empty lines
                    if line.startswith("data: "):
                        line = line[6:]  # Remove "data: " prefix

                    # Skip [DONE] marker
                    if line.strip() == "[DONE]":
                        continue

                    try:
                        # Try to parse as JSON
                        chunk = json.loads(line)

                        # Handle OpenAI-compatible format (primary format from RAG server)
                        if "choices" in chunk and isinstance(chunk["choices"], list) and len(chunk["choices"]) > 0:
                            choice = chunk["choices"][0]
                            if "delta" in choice and isinstance(choice["delta"], dict):
                                content = choice["delta"].get("content", "")
                                if content:
                                    yield content
                                # Check for finish reason
                                if choice.get("finish_reason") in ["stop", "error"]:
                                    continue
                        # Handle alternative formats for backward compatibility
                        elif "content" in chunk:
                            # Direct content field
                            content = chunk["content"]
                            if content:
                                yield content
                        elif "chunk" in chunk:
                            # Chunked response
                            content = chunk["chunk"]
                            if content:
                                yield content
                        elif "response" in chunk:
                            # Full response field (for compatibility)
                            content = chunk["response"]
                            if content:
                                yield content
                        elif "text" in chunk:
                            # Text field
                            content = chunk["text"]
                            if content:
                                yield content

                    except json.JSONDecodeError:
                        # If not JSON, yield as plain text
                        if line.strip():
                            yield line

        except requests.exceptions.RequestException as e:
            yield f"\n\nError during RAG query: {str(e)}"
        except Exception as e:
            yield f"\n\nUnexpected error: {str(e)}"
