"""FastAPI Application - CloudWalk Agent Swarm"""
# IMPORTANTE: Carregar variáveis de ambiente PRIMEIRO
from src.env_loader import *  # noqa: F401, F403

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.config import settings
from src.schemas import ChatRequest, ChatResponse

# Setup logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager - executa no startup e shutdown
    """
    # === STARTUP ===
    logger.info("="*80)
    logger.info("INICIALIZANDO APLICACAO")
    logger.info("="*80)
    
    # 1. Seed database SQLite (se necessário)
    logger.info("Verificando banco de dados SQLite...")
    try:
        from scripts.seed_db import seed_if_empty
        seed_if_empty()
    except Exception as e:
        logger.warning(f"Erro ao verificar/seed database: {e}")
    
    # 2. Validar RAG Pipeline (ChromaDB deve estar populado)
    logger.info("Validando RAG pipeline...")
    try:
        from src.rag.ingest import validate_rag_completeness
        validate_rag_completeness()
        logger.info("[OK] RAG pipeline validado e pronto")
    except Exception as e:
        logger.error("="*80)
        logger.error("ERRO: RAG Pipeline nao esta pronto!")
        logger.error(f"Motivo: {e}")
        logger.error("")
        logger.error("SOLUCAO:")
        logger.error("  1. Execute: python scripts/ingest_rag.py")
        logger.error("  2. Aguarde a ingestao completa")
        logger.error("  3. Reinicie a aplicacao")
        logger.error("="*80)
        raise RuntimeError("ChromaDB nao esta pronto. Execute 'python scripts/ingest_rag.py' primeiro.")
    
    logger.info("="*80)
    logger.info("[OK] APLICACAO PRONTA")
    logger.info("="*80)
    
    yield
    
    # === SHUTDOWN ===
    logger.info("Encerrando aplicacao...")


# Create app with lifespan
app = FastAPI(
    title="CloudWalk Agent Swarm",
    description="Sistema multi-agente com RAG para InfinitePay",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve Frontend
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path

frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/app", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


@app.get("/")
async def root():
    """Redirect to frontend app"""
    return RedirectResponse(url="/app/index.html")


@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "service": "CloudWalk Agent Swarm"
    }


@app.post("/chat")
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Unified chat endpoint - Routes through the Agent Swarm.
    
    The Router Agent analyzes the query and decides which specialized agent(s)
    to invoke (Knowledge, Support, or both).
    """
    from src.agents.router_agent import route_query
    
    logger.info(f"[/chat] User: {request.user_id} | Query: {request.message}")
    
    try:
        # Route query through the Agent Swarm
        result = route_query(
            query=request.message,
            user_id=request.user_id
        )
        
        # Format response
        response = ChatResponse(
            response=result["response"],
            agent_used=result["agent_used"],
            sources=result.get("sources", [])
        )
        
        logger.info(f"[/chat] Routed to: {result.get('routing', 'unknown')} | Agents: {result['agent_used']}")
        return response
        
    except Exception as e:
        logger.error(f"[/chat] Erro: {e}", exc_info=True)
        # Return formatted error
        return ChatResponse(
            response=f"Erro ao processar sua mensagem: {str(e)}",
            agent_used="error",
            sources=[]
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development"
    )

