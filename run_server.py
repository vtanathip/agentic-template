"""
Run the FastAPI server for the agentic template.

Usage:
    python run_server.py
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Run the FastAPI server."""
    # Get the path to the server module
    project_root = Path(__file__).parent
    server_path = project_root / "src" / "server" / "main.py"
    
    if not server_path.exists():
        print(f"Error: Server file not found at {server_path}")
        sys.exit(1)
    
    print("Starting FastAPI server...")
    print("API will be available at: http://localhost:8000")
    print("API docs will be available at: http://localhost:8000/docs")
    print("Press CTRL+C to stop the server")
    print("-" * 50)
    
    try:
        # Run the server using uv
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "src.server.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Error running server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()