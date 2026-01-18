"""
RAG Searcher - Interface for semantic search in ChromaDB

Provides semantic search with context formatting for LLM usage
"""

import chromadb
from typing import List, Dict, Optional
import logging
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from src.config import settings

logger = logging.getLogger(__name__)


class RAGSearcher:
    """Interface for searching documents in ChromaDB"""
    
    def __init__(self):
        """Initializes searcher with ChromaDB and embeddings"""
        logger.info("Initializing RAGSearcher...")
        
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
        
        logger.info("RAGSearcher ready")
    
    def search(
        self, 
        query: str, 
        top_k: int = 5,
        filter_by: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Semantic search in ChromaDB
        
        Args:
            query: Query text
            top_k: Number of results to return (default: 5)
            filter_by: Metadata filters (optional)
                Example: {"product": "maquininha"}
        
        Returns:
            List of dicts with:
            - content: chunk text
            - metadata: dict with product, section, source, etc
            - score: similarity score
        """
        logger.debug(f"Searching: '{query}' (top_k={top_k})")
        
        # Similarity search
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
        
        # Format results
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                'content': doc.page_content,
                'metadata': doc.metadata,
                'score': float(score)
            })
        
        logger.info(f"Found {len(formatted_results)} results")
        return formatted_results
    
    def format_context(self, documents: List[Dict], include_metadata: bool = True) -> str:
        """
        Formats documents as context for LLM
        
        Args:
            documents: List of documents (search() result)
            include_metadata: If True, includes header and source
        
        Returns:
            Formatted string for context usage
        """
        if not documents:
            return "No relevant documents found."
        
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            content = doc['content']
            metadata = doc.get('metadata', {})
            
            if include_metadata:
                header = metadata.get('section', 'Untitled')
                source = metadata.get('source', 'Unknown source')
                product = metadata.get('product', '')
                
                # Format each document
                doc_text = f"""
[DOCUMENT {i}]
Product: {product}
Section: {header}
Source: {source}

{content}
---
"""
            else:
                doc_text = f"\n[DOCUMENT {i}]\n{content}\n---\n"
            
            context_parts.append(doc_text)
        
        return '\n'.join(context_parts)
    
    def search_and_format(
        self, 
        query: str, 
        top_k: int = 5,
        include_metadata: bool = True
    ) -> tuple[str, List[Dict]]:
        """
        Search and format in a single operation
        
        Args:
            query: Search query
            top_k: Number of results
            include_metadata: Include metadata in context
        
        Returns:
            Tuple (formatted_context, raw_documents)
        """
        documents = self.search(query, top_k=top_k)
        context = self.format_context(documents, include_metadata=include_metadata)
        return context, documents

