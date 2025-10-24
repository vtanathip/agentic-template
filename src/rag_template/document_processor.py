"""
Document processor using Docling for high-quality document extraction and processing.
"""

import os
import tempfile
from typing import List, Dict, Any, BinaryIO
from pathlib import Path

try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import InputFormat
except ImportError:
    DocumentConverter = None
    InputFormat = None


class DoclingProcessor:
    """Document processor using Docling for advanced document extraction."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize the Docling processor.

        Args:
            chunk_size: Maximum size of each text chunk in characters.
            chunk_overlap: Number of characters to overlap between chunks.
        """
        if DocumentConverter is None:
            raise ImportError(
                "Docling package is required for document processing")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.converter = DocumentConverter()

    def process_file(self, file_content: BinaryIO, filename: str) -> List[Dict[str, Any]]:
        """Process an uploaded file and return document chunks.

        Args:
            file_content: Binary file content.
            filename: Name of the uploaded file.

        Returns:
            List of document chunks with metadata.
        """
        # Determine file type
        file_extension = Path(filename).suffix.lower()

        # Check if file type is supported
        supported_formats = ['.pdf', '.docx', '.doc', '.txt', '.md', '.html']
        if file_extension not in supported_formats:
            raise ValueError(
                f"Unsupported file type: {file_extension}. Supported: {supported_formats}")

        # Save file content to temporary file for Docling
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            tmp_file.write(file_content.read())
            tmp_path = tmp_file.name

        try:
            # Handle text files separately since Docling doesn't support plain .txt
            if file_extension == '.txt':
                # Read text file directly
                with open(tmp_path, 'r', encoding='utf-8') as f:
                    text = f.read()

                metadata = {
                    "filename": filename,
                    "file_type": file_extension,
                    "source": filename,
                    "page_count": 1,
                    "title": filename,
                    "document_id": filename,  # Unique document identifier
                }
            else:
                # Convert document using Docling
                result = self.converter.convert(tmp_path)

                # Extract text content
                text = result.document.export_to_markdown()

                # Extract metadata
                metadata = {
                    "filename": filename,
                    "file_type": file_extension,
                    "source": filename,
                    "page_count": len(result.document.pages) if hasattr(result.document, 'pages') else 1,
                    "title": getattr(result.document, 'title', filename),
                    "document_id": filename,  # Unique document identifier
                }

        finally:
            # Clean up temporary file
            os.unlink(tmp_path)

        # Split text into chunks
        chunks = self._split_text(text)

        # Create document chunks with metadata
        documents = []
        for i, chunk in enumerate(chunks):
            documents.append({
                "id": f"{filename}_{i}",
                "text": chunk,
                "source": filename,
                "chunk_index": i,
                "metadata": {
                    **metadata,
                    "chunk_size": len(chunk),
                    "total_chunks": len(chunks)
                }
            })

        return documents

    def _split_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks with smart boundaries."""
        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # If we're not at the end, try to break at a good boundary
            if end < len(text):
                # Look for paragraph break first
                paragraph_end = text.rfind('\n\n', start, end)
                if paragraph_end != -1 and paragraph_end > start + self.chunk_size // 2:
                    end = paragraph_end + 2
                else:
                    # Look for sentence ending
                    sentence_end = text.rfind('.', start, end)
                    if sentence_end != -1 and sentence_end > start + self.chunk_size // 2:
                        end = sentence_end + 1
                    else:
                        # Look for word boundary
                        word_end = text.rfind(' ', start, end)
                        if word_end != -1 and word_end > start + self.chunk_size // 2:
                            end = word_end

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move start position with overlap
            start = max(start + 1, end - self.chunk_overlap)

            # Prevent infinite loop
            if start >= len(text):
                break

        return chunks

    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return ['.pdf', '.docx', '.doc', '.txt', '.md', '.html']
