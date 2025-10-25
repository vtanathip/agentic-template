"""
title: LangGraph Agentic RAG Pipeline
author: vtanathip
author_url: https://github.com/vtanathip
git_url: https://github.com/vtanathip/agentic-template
description: OpenWebUI Pipeline for LangGraph Agentic RAG with streaming support and file upload capability
required_open_webui_version: 0.4.3
requirements: requests
        version="2.3.1",  # Added simple waiting message indicator
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
        OPENWEBUI_URL: str = Field(
            default="http://openwebui:8080",
            description="Base URL for OpenWebUI (for downloading uploaded files)"
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

    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """
        Process incoming requests before they reach the pipe method.
        This is where we handle file uploads to the RAG system.

        Args:
            body: Request body containing messages and potentially files
            user: User information (optional)

        Returns:
            Modified body with file upload results
        """
        print(f"inlet: Processing request")
        print(f"inlet: Body keys: {body.keys()}")

        # Check if there are any files in the messages
        messages = body.get("messages", [])
        print(f"inlet: Number of messages: {len(messages)}")

        for idx, message in enumerate(messages):
            print(
                f"inlet: Message {idx} - role: {message.get('role')}, content type: {type(message.get('content'))}")

            # Handle both string and list content formats
            content = message.get("content")

            # If content is a string, check for files in body level
            if isinstance(content, str):
                # Check if there are files at the body level
                if "files" in body:
                    files_list = body.get("files", [])
                    print(
                        f"inlet: Found {len(files_list)} files in body.files")

                    for file_info in files_list:
                        try:
                            print(f"📎 Found file to upload: {file_info}")

                            # Get file path from OpenWebUI - it's already saved locally
                            file_path = file_info.get(
                                "file", {}).get("path", "")
                            filename = file_info.get("name") or file_info.get(
                                "file", {}).get("filename", "") or "uploaded_file"

                            if not file_path:
                                print(
                                    f"⚠️  No file path found in: {file_info}")
                                continue

                            print(
                                f"📤 Reading file: {filename} from {file_path}")

                            # Read the file directly from disk (shared volume)
                            try:
                                with open(file_path, 'rb') as f:
                                    file_content = f.read()
                                print(
                                    f"✅ File read successfully: {len(file_content)} bytes")
                            except FileNotFoundError:
                                print(f"❌ File not found at path: {file_path}")
                                continue
                            except Exception as read_error:
                                print(
                                    f"❌ Error reading file: {str(read_error)}")
                                continue

                            # Upload to RAG server
                            upload_url = f"{self.valves.RAG_API_URL}/upload"
                            files = {"file": (filename, file_content)}

                            print(f"📤 Uploading to RAG server: {filename}")
                            upload_response = requests.post(
                                upload_url,
                                files=files,
                                timeout=self.valves.TIMEOUT
                            )
                            upload_response.raise_for_status()

                            result = upload_response.json()

                            if result.get("success"):
                                print(
                                    f"✅ File uploaded successfully: {filename}")
                                # Add confirmation to message content
                                upload_msg = f"\n\n[File '{filename}' uploaded successfully to knowledge base]"
                                message["content"] = content + upload_msg
                            else:
                                error_msg = result.get(
                                    "error", "Unknown error")
                                print(f"❌ File upload failed: {error_msg}")

                        except Exception as e:
                            error_msg = f"Error processing file: {str(e)}"
                            print(f"❌ {error_msg}")
                            import traceback
                            traceback.print_exc()

            # Handle list content format (original implementation)
            elif isinstance(content, list):
                print(
                    f"inlet: Message {idx} has list content with {len(content)} items")
                for content_idx, content_item in enumerate(content):
                    print(f"inlet: Content item {content_idx}: {content_item}")

                    if isinstance(content_item, dict) and content_item.get("type") == "file":
                        # Extract file information
                        file_url = content_item.get("url", "")

                        if file_url:
                            try:
                                # If URL is relative, make it absolute
                                if file_url.startswith("/"):
                                    file_url = f"{self.valves.OPENWEBUI_URL}{file_url}"

                                print(f"📎 Found file to upload: {file_url}")

                                # Download the file from the URL
                                file_response = requests.get(
                                    file_url, timeout=30)
                                file_response.raise_for_status()

                                # Extract filename from URL or use default
                                filename = file_url.split(
                                    "/")[-1] or "uploaded_file"

                                # Upload to RAG server
                                upload_url = f"{self.valves.RAG_API_URL}/upload"
                                files = {
                                    "file": (filename, file_response.content)
                                }

                                print(f"📤 Uploading to RAG server: {filename}")
                                upload_response = requests.post(
                                    upload_url,
                                    files=files,
                                    timeout=self.valves.TIMEOUT
                                )
                                upload_response.raise_for_status()

                                result = upload_response.json()

                                if result.get("success"):
                                    print(
                                        f"✅ File uploaded successfully: {filename}")

                                    # Add upload confirmation to the message
                                    upload_msg = f"\n\n[File '{filename}' uploaded successfully to knowledge base]"

                                    # Find the user message and append confirmation
                                    if message.get("role") == "user":
                                        # Get the text content
                                        text_content = ""
                                        for item in message["content"]:
                                            if isinstance(item, dict) and item.get("type") == "text":
                                                text_content = item.get(
                                                    "text", "")
                                                break

                                        # Update the message to include upload confirmation
                                        message["content"] = text_content + \
                                            upload_msg
                                else:
                                    error_msg = result.get(
                                        "error", "Unknown error")
                                    print(f"❌ File upload failed: {error_msg}")
                                    message["content"] = f"Error uploading file: {error_msg}"

                            except Exception as e:
                                error_msg = f"Error processing file: {str(e)}"
                                print(f"❌ {error_msg}")
                                import traceback
                                traceback.print_exc()

        return body

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
        Stream RAG query results to the frontend with simple waiting indicator.

        Shows a static "Searching..." message, then streams the actual response.

        Args:
            user_message: The user's question
            messages: Conversation history

        Yields:
            Text chunks as they are generated
        """
        # Show simple thinking message
        yield "🔍 Searching documents and generating response...\n\n"
        
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
