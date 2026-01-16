"""Configurações da aplicação carregadas do .env"""
# IMPORTANTE: env_loader DEVE ser importado primeiro para carregar variáveis de ambiente
from src.env_loader import *  # noqa: F401, F403

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # OpenAI (OBRIGATÓRIA)
    openai_api_key: str = Field(..., description="API key da OpenAI")
    
    # Tavily (Opcional, mas necessária para Knowledge Agent)
    tavily_api_key: str | None = Field(default=None, description="API key da Tavily")
    
    # Application
    environment: str = Field(default="development", description="Ambiente de execução")
    log_level: str = Field(default="INFO", description="Nível de logging")
    api_host: str = Field(default="0.0.0.0", description="Host da API")
    api_port: int = Field(default=8000, description="Porta da API")
    
    # Paths
    chroma_persist_dir: str = Field(
        default="./data/chromadb",
        description="Diretório de persistência do ChromaDB"
    )
    sqlite_db_path: str = Field(
        default="data/customers.db",
        description="Path to SQLite database"
    )
    
    # LLM Config
    default_model: str = Field(default="gpt-4o-mini", description="Modelo LLM padrão")
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="Modelo de embeddings"
    )
    max_tokens: int = Field(default=1000, description="Máximo de tokens por resposta")
    temperature: float = Field(default=0.7, description="Temperature do LLM")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instância global
settings = Settings()

