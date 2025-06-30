#!/usr/bin/env python3
"""
Main entry point for the text-to-image application
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the FastAPI app from the app module
from app.main import app

if __name__ == "__main__":
    import uvicorn
    # Get port from environment variable (Railway sets this)
    port = int(os.getenv("PORT", 3123))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 