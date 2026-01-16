"""
Entry point da aplicação - Garante carregamento correto de variáveis de ambiente

Execute com: python -m src.main
ou para desenvolvimento: python -m uvicorn src.main:app --reload
"""

# PRIMEIRO: Carregar variáveis de ambiente
from src.env_loader import *  # noqa: F401, F403

import os
print("\n" + "="*80)
print("VERIFICACAO DE VARIAVEIS DE AMBIENTE")
print("="*80)
print(f"OPENAI_API_KEY carregada: {bool(os.environ.get('OPENAI_API_KEY'))}")
print(f"ENVIRONMENT: {os.environ.get('ENVIRONMENT', 'development')}")
print("="*80 + "\n")

# Agora importar a aplicação
if __name__ == "__main__":
    from src.main import app
    import uvicorn
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=True
    )

