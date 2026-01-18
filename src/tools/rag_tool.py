from crewai.tools import BaseTool
from src.rag.search import RAGSearcher
import logging
from typing import Any, Type
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Global searcher instance
_searcher = None

def get_rag_searcher():
    """Lazy initialization of RAGSearcher"""
    # ... (same)
    global _searcher
    if _searcher is None:
        _searcher = RAGSearcher()
        logger.info("RAG Searcher initialized")
    return _searcher

class RagToolInput(BaseModel):
    query: str = Field(..., description="The search query. This is the ONLY accepted argument.")

class RagTool(BaseTool):
    name: str = "search_infinitepay_knowledge"
    description: str = """
    Searches for detailed information about InfinitePay products, services, and fees.
    Input must be a JSON object with a single key 'query'.
    """
    args_schema: Type[BaseModel] = RagToolInput

    def _run(self, query: str) -> str:
        logger.info(f"RAG Tool executing search: '{query}'")
        try:
            searcher = get_rag_searcher()
            context, documents = searcher.search_and_format(
                query=query,
                top_k=3,
                include_metadata=True
            )
            sources = set([doc['metadata'].get('source', 'unknown') for doc in documents])
            from src.utils.debug_tracker import log_tool_usage
            
            logger.info(f"RAG Tool returned {len(documents)} documents from {len(sources)} URLs")
            
            log_tool_usage(
                tool_name="RAG (InfinitePay)",
                input_str=query,
                output_str=f"Found {len(documents)} docs. Sources: {list(sources)}",
                metadata={"docs_count": len(documents), "sources": list(sources)}
            )
            
            return context
        except Exception as e:
            logger.error(f"Error executing RAG search: {e}", exc_info=True)
            return f"Error searching information: {str(e)}"

# Instantiate for import
rag_search_tool = RagTool()

# Legacy alias
search_infinitepay_knowledge = rag_search_tool.run

