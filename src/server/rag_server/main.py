"""
Launcher script for the RAG server.
"""

import uvicorn
from server.rag_server.app import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,  # Use different port from main server
        reload=True
    )
