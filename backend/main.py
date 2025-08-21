import logging
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from routers import chat, search
from config.settings import get_settings

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting Semantix Chat application")
    yield
    logger.info("Shutting down Semantix Chat application")

# Initialize FastAPI app
app = FastAPI(
    title="Semantix Chat API",
    description="ChatGPT-like API with multiple LLM support",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(search.router, prefix="/search", tags=["search"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Semantix Chat API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    settings = get_settings()
    return {
        "status": "healthy",
        "version": "1.0.0",
        "models_available": {
            "openai": bool(settings.openai_api_key),
            "anthropic": bool(settings.anthropic_api_key)
        }
    }

if __name__ == "__main__":
    settings = get_settings()
    logger.info(f"Starting server on port {settings.port}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower()
    )