"""
Script standalone para popular ChromaDB

USO:
    python scripts/ingest_rag.py
    
Roda UMA VEZ durante desenvolvimento para popular ChromaDB.
Depois, commita data/chromadb/ no Git para que container já venha com dados.
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.ingest import ingest_documents


def main():
    """Executa ingestão RAG"""
    print("\n" + "="*80)
    print("SCRIPT: Ingestao RAG para ChromaDB")
    print("="*80 + "\n")
    
    try:
        count = ingest_documents()
        
        print("\n" + "="*80)
        print(f"[SUCESSO] {count} chunks ingeridos com sucesso!")
        print("="*80)
        print("\nProximos passos:")
        print("  1. Verificar: ls data/chromadb/")
        print("  2. Commitar: git add data/chromadb/")
        print("  3. Testar: python -m uvicorn src.main:app --reload")
        print("")
        
        return 0
        
    except Exception as e:
        print("\n" + "="*80)
        print(f"[ERRO] Ingestao falhou!")
        print(f"Motivo: {e}")
        print("="*80 + "\n")
        
        import traceback
        traceback.print_exc()
        
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

