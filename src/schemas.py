"""Pydantic Models para validação de API"""
from pydantic import BaseModel, Field
from typing import List, Optional


class ChatRequest(BaseModel):
    """Request para o endpoint /chat"""
    message: str = Field(..., description="Mensagem do usuário", min_length=1)
    user_id: str = Field(..., description="Identificador do usuário")
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "message": "Quais as taxas da maquininha smart?",
                "user_id": "client789"
            }]
        }
    }


class ChatResponse(BaseModel):
    """Response do endpoint /chat"""
    response: str = Field(..., description="Resposta gerada pelo agente")
    agent_used: List[str] = Field(..., description="Lista de agentes que processaram a requisição")
    sources: List[str] = Field(
        default_factory=list,
        description="Fontes consultadas (URLs ou referências)"
    )
    debug_info: Optional[dict] = Field(
        default=None,
        description="Informações de debug do processamento (logs, tools, routing)"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "response": "A Maquininha Smart tem taxa de 1,99% no débito...",
                "agent_used": ["knowledge"],
                "sources": ["https://www.infinitepay.io/maquininha"],
                "debug_info": {
                    "routing": "KNOWLEDGE",
                    "language": "Portuguese",
                    "logs": []
                }
            }]
        }
    }


class UserCreateRequest(BaseModel):
    """Request for creating a new user"""
    name: str = Field(..., description="User's name", min_length=1)
    user_id: Optional[str] = Field(None, description="Optional user ID (auto-generated if not provided)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "name": "João Silva",
                "user_id": "joao_silva_123"
            }]
        }
    }


class UserResponse(BaseModel):
    """Response after user creation"""
    user_id: str = Field(..., description="User identifier")
    name: str = Field(..., description="User's name")
    balance: float = Field(..., description="Account balance")
    account_status: str = Field(..., description="Account status")
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "user_id": "joao_silva_123",
                "name": "João Silva",
                "balance": 0.0,
                "account_status": "active"
            }]
        }
    }


