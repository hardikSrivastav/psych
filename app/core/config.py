import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str
    
    # Service URLs
    qdrant_url: str = "http://qdrant:6333"
    redis_url: str = "redis://redis:6379"
    
    # Application Configuration
    log_level: str = "INFO"
    session_ttl_hours: int = 24
    max_conversation_length: int = 10
    
    # Development Configuration
    debug: bool = False
    
    # Vector Database Configuration
    collection_name: str = "psychology_papers"
    vector_size: int = 3072  # text-embedding-3-large
    similarity_threshold: float = 0.3  # Lowered for testing with small dataset
    chunks_per_query: int = 5
    
    # Redis Configuration
    redis_max_memory: str = "256mb"
    redis_memory_policy: str = "allkeys-lru"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
