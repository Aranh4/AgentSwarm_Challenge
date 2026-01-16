"""
RAG Searcher - Interface para busca semântica no ChromaDB

Fornece busca semântica com formatação de contexto para uso em LLMs
"""

import chromadb
from typing import List, Dict, Optional
import logging
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from src.config import settings

logger = logging.getLogger(__name__)


class RAGSearcher:
    """Interface para buscar documentos no ChromaDB"""
    
    def __init__(self):
        """Inicializa searcher com ChromaDB e embeddings"""
        logger.info("Inicializando RAGSearcher...")
        
        # Setup embeddings
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        # Load vectorstore
        self.vectorstore = Chroma(
            collection_name="infinitepay_docs",
            embedding_function=self.embeddings,
            persist_directory=settings.chroma_persist_dir
        )
        
        logger.info("RAGSearcher pronto")
    
    def search(
        self, 
        query: str, 
        top_k: int = 5,
        filter_by: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Busca semântica no ChromaDB
        
        Args:
            query: Texto da query
            top_k: Número de resultados a retornar (padrão: 5)
            filter_by: Filtros de metadata (opcional)
                Exemplo: {"product": "maquininha"}
        
        Returns:
            Lista de dicts com:
            - content: texto do chunk
            - metadata: dict com product, section, source, etc
            - score: score de similaridade
        """
        logger.debug(f"Buscando: '{query}' (top_k={top_k})")
        
        # Busca por similaridade
        if filter_by:
            results = self.vectorstore.similarity_search_with_score(
                query,
                k=top_k,
                filter=filter_by
            )
        else:
            results = self.vectorstore.similarity_search_with_score(
                query,
                k=top_k
            )
        
        # Formatar resultados
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                'content': doc.page_content,
                'metadata': doc.metadata,
                'score': float(score)
            })
        
        logger.info(f"Encontrados {len(formatted_results)} resultados")
        return formatted_results
    
    def format_context(self, documents: List[Dict], include_metadata: bool = True) -> str:
        """
        Formata documentos como contexto para LLM
        
        Args:
            documents: Lista de documentos (resultado de search())
            include_metadata: Se True, inclui header e source
        
        Returns:
            String formatada para uso como contexto
        """
        if not documents:
            return "Nenhum documento relevante encontrado."
        
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            content = doc['content']
            metadata = doc.get('metadata', {})
            
            if include_metadata:
                header = metadata.get('section', 'Sem título')
                source = metadata.get('source', 'Fonte desconhecida')
                product = metadata.get('product', '')
                
                # Formatar cada documento
                doc_text = f"""
[DOCUMENTO {i}]
Produto: {product}
Seção: {header}
Fonte: {source}

{content}
---
"""
            else:
                doc_text = f"\n[DOCUMENTO {i}]\n{content}\n---\n"
            
            context_parts.append(doc_text)
        
        return '\n'.join(context_parts)
    
    def search_and_format(
        self, 
        query: str, 
        top_k: int = 5,
        include_metadata: bool = True
    ) -> tuple[str, List[Dict]]:
        """
        Busca e formata em uma única operação
        
        Args:
            query: Query para buscar
            top_k: Número de resultados
            include_metadata: Incluir metadata no contexto
        
        Returns:
            Tupla (contexto_formatado, documentos_raw)
        """
        documents = self.search(query, top_k=top_k)
        context = self.format_context(documents, include_metadata=include_metadata)
        return context, documents

