"""FastAPI Application - CloudWalk Agent Swarm"""
# IMPORTANT: Load environment variables FIRST
from src.env_loader import *  # noqa: F401, F403

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.config import settings
from src.schemas import ChatRequest, ChatResponse, UserCreateRequest, UserResponse
from src.utils.session_manager import session_manager

# Setup logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager - runs on startup and shutdown
    """
    # === STARTUP ===
    logger.info("="*80)
    logger.info("INITIALIZING APPLICATION")
    logger.info("="*80)
    
    # 1. Seed database SQLite (if necessary)
    logger.info("Checking SQLite database...")
    try:
        from scripts.seed_db import seed_if_empty
        seed_if_empty()
    except Exception as e:
        logger.warning(f"Error checking/seeding database: {e}")
    
    # 2. Validate RAG Pipeline (ChromaDB must be populated)
    logger.info("Validating RAG pipeline...")
    try:
        from src.rag.ingest import validate_rag_completeness, ingest_documents
        validate_rag_completeness()
        logger.info("[OK] RAG pipeline valid and ready")
    except Exception as e:
        logger.warning(f"RAG Pipeline not ready ({e}). Starting auto-ingestion...")
        logger.info("This process may take a few minutes (scraping 18 URLs)...")
        try:
            ingest_documents()
            logger.info("[OK] Auto-ingestion completed successfully!")
        except Exception as ingest_error:
            logger.error("="*80)
            logger.error("CRITICAL ERROR: Failed to initialize RAG pipeline!")
            logger.error(f"Reason: {ingest_error}")
            logger.error("="*80)
            raise RuntimeError(f"Could not build RAG knowledge base: {ingest_error}")
    
    logger.info("="*80)
    logger.info("[OK] APPLICATION READY")
    logger.info("="*80)
    
    yield
    
    # === SHUTDOWN ===
    logger.info("Shutting down application...")


# Create app with lifespan
app = FastAPI(
    title="CloudWalk Agent Swarm",
    description="Multi-agent system with RAG for InfinitePay",
    version="1.0.0",
    lifespan=lifespan,
    debug=True
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
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "service": "CloudWalk Agent Swarm"
    }


@app.post("/users", response_model=UserResponse)
async def create_user(request: UserCreateRequest):
    """
    Create a new user in the database
    
    Allows frontend to register new users with custom or auto-generated IDs.
    Users are initialized with zero balance and empty transaction history.
    """
    import sqlite3
    import uuid
    from datetime import datetime
    
    logger.info(f"[/users] Creating user: {request.name}")
    
    try:
        # Generate user_id if not provided
        user_id = request.user_id if request.user_id else str(uuid.uuid4())[:8]
        
        # Connect to database
        conn = sqlite3.connect("./data/customers.db")
        cursor = conn.cursor()
        
        # Check for duplicate
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if cursor.fetchone():
            conn.close()
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=f"User ID '{user_id}' already exists")
        
        # Insert new user
        cursor.execute(
            """
            INSERT INTO users (user_id, name, email, account_status, plan, balance, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, request.name, "", "active", "basic", 0.0, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        
        logger.info(f"[/users] User created: {user_id}")
        
        return UserResponse(
            user_id=user_id,
            name=request.name,
            balance=0.0,
            account_status="active"
        )
        
    except Exception as e:
        logger.error(f"[/users] Error: {e}", exc_info=True)
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Unified chat endpoint - Routes through the Agent Swarm.
    
    The Router Agent analyzes the query and decides which specialized agent(s)
    to invoke (Knowledge, Support, or both).
    """
    from src.agents.router_agent import route_query
    from src.utils.debug_tracker import init_tracker, get_current_debug_info
    
    # Initialize debug tracker for this request
    init_tracker()
    
    logger.info(f"[/chat] User: {request.user_id} | Query: {request.message}")
    
    try:
        # HARDENING: Security Guardrail Check
        from src.agents.guardrail_agent import validate_input
        security_check = validate_input(request.message, request.user_id)
        
        if security_check.get("status") == "BLOCKED":
            from src.utils.debug_tracker import set_guardrail_status
            set_guardrail_status("BLOCKED")
            
            block_reason = security_check.get("reason", "Security Policy Violation")
            user_message = security_check.get("message", f"Sorry, I cannot process this request due to safety policies ({block_reason}).")
            
            logger.warning(f"[/chat] BLOCKED: {block_reason}")
            
            # Return with debug info even if blocked
            return ChatResponse(
                response=user_message,
                agent_used=["guardrail"],
                sources=[],
                debug_info=get_current_debug_info()
            )

        # Route query through the Agent Swarm
        result = route_query(
            query=request.message,
            user_id=request.user_id
        )
        
        # Format response
        response = ChatResponse(
            response=result["response"],
            agent_used=result["agent_used"],
            sources=result.get("sources", []),
            debug_info=get_current_debug_info()
        )
        
        logger.info(f"[/chat] Routed to: {result.get('routing', 'unknown')} | Agents: {result['agent_used']}")
        
        # Store message in session for context
        session_manager.add_message(
            user_id=request.user_id,
            query=request.message,
            response=result["response"]
        )
        
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

