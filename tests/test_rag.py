"""
test_rag.py - RAG Pipeline tests
Tests the ChromaDB vector store and retrieval functionality.
"""
import pytest


class TestRAGPipeline:
    """Tests for RAG pipeline components."""
    
    def test_chromadb_has_documents(self):
        """ChromaDB should have indexed documents."""
        from src.rag.ingest import create_chroma_client
        
        client = create_chroma_client()
        collection = client.get_collection("infinitepay_docs")
        count = collection.count()
        
        assert count > 0, "ChromaDB should have documents"
        print(f"ChromaDB has {count} documents")
    
    def test_rag_searcher_returns_results(self):
        """RAGSearcher should return relevant results."""
        from src.rag.search import RAGSearcher
        
        searcher = RAGSearcher()
        results = searcher.search("maquininha smart taxas")
        
        assert len(results) > 0, "Should find relevant documents"
        assert "content" in results[0]
    
    def test_rag_search_and_format(self):
        """RAGSearcher.search_and_format should return formatted context."""
        from src.rag.search import RAGSearcher
        
        searcher = RAGSearcher()
        context, docs = searcher.search_and_format("Pix InfinitePay")
        
        assert len(context) > 0
        assert isinstance(context, str)
        assert len(docs) > 0


class TestRAGTool:
    """Tests for the CrewAI RAG tool."""
    
    def test_rag_tool_function_exists(self):
        """RAG tool function should exist."""
        from src.tools.rag_tool import search_infinitepay_knowledge
        
        assert callable(search_infinitepay_knowledge)
    
    def test_rag_tool_returns_content(self):
        """RAG tool should return content when called."""
        from src.tools.rag_tool import search_infinitepay_knowledge
        
        result = search_infinitepay_knowledge("taxas maquininha")
        
        assert isinstance(result, str)
        assert len(result) > 0
