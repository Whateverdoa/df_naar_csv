#!/usr/bin/env python3
"""
Development server runner for FastAPI application
"""
import uvicorn
from app.main import app

def main():
    """Entry point for the run-api console script."""
    print("Starting DF naar CSV FastAPI server...")
    print("API Documentation: http://localhost:8000/docs")
    print("Alternative docs: http://localhost:8000/redoc")
    print("Health check: http://localhost:8000/health")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )


if __name__ == "__main__":
    main()
