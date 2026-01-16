"""
Loader de ambiente - DEVE ser importado PRIMEIRO em toda aplicação

Carrega .env para variáveis de ambiente do sistema antes de qualquer outro import.
Isso garante que CrewAI, LangChain e outras libs encontrem as variáveis.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar .env para variáveis de ambiente do sistema
env_file = Path(__file__).parent.parent / ".env"
load_dotenv(env_file, override=True)

print(f"[INIT] Variáveis de ambiente carregadas de {env_file}")
print(f"[INIT] OPENAI_API_KEY presente: {'OPENAI_API_KEY' in os.environ}")

