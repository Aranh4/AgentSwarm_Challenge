"""Application settings loaded from .env"""
# IMPORTANT: env_loader MUST be imported first to load environment variables
from src.env_loader import *  # noqa: F401, F403

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application Settings"""
    
    # OpenAI (REQUIRED)
    openai_api_key: str = Field(..., description="OpenAI API key")
    
    # Tavily (Optional, but required for Knowledge Agent)
    tavily_api_key: str | None = Field(default=None, description="Tavily API key")
    
    # Application
    environment: str = Field(default="development", description="Execution environment")
    log_level: str = Field(default="INFO", description="Logging level")
    api_host: str = Field(default="0.0.0.0", description="API Host")
    api_port: int = Field(default=8080, description="API Port")
    
    # Paths
    chroma_persist_dir: str = Field(
        default="./data/chromadb",
        description="ChromaDB persistence directory"
    )
    sqlite_db_path: str = Field(
        default="data/customers.db",
        description="Path to SQLite database"
    )
    
    # LLM Config
    default_model: str = Field(default="gpt-4o-mini", description="Default LLM model")
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="Embedding model"
    )
    max_tokens: int = Field(default=1000, description="Max tokens per response")
    temperature: float = Field(default=0.7, description="LLM Temperature")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global instance
settings = Settings()

