import os
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    port: int = int(os.getenv("PORT", "5669"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    supported_file_types: list = [".pdf", ".txt"]
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()