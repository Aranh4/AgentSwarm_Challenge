"""Pydantic Models para validação de API"""
from pydantic import BaseModel, Field
from typing import List


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
    agent_used: str = Field(..., description="Nome do agente que processou")
    sources: List[str] = Field(
        default_factory=list,
        description="Fontes consultadas (URLs ou referências)"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "response": "A Maquininha Smart tem taxa de 1,99% no débito...",
                "agent_used": "Knowledge Agent",
                "sources": ["https://www.infinitepay.io/maquininha"]
            }]
        }
    }

