"""
Main entry point for the QA System application
"""

import uvicorn
from src.qa_system.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "src.qa_system.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )