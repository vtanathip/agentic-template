#!/usr/bin/env python3
"""Startup script for the Multi-Agent Trading System API."""

import uvicorn
from src.server.multiagent_api.main import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
