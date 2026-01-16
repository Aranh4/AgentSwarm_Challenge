"""
WebSearch Tool - Web search using DuckDuckGo

Tool to search for general information on the web when:
- The question is NOT about InfinitePay internals
- RAG does not have enough information
- Questions about current events, news, sports, competitors, etc.
"""

import logging
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)


def search_web(query: str, max_results: int = 5) -> str:
    """
    Searches information on the web using DuckDuckGo.
    
    Use for:
    - General questions not related to InfinitePay internal details
    - News, current events, sports, weather
    - Competitor analysis (searching for competitor rates, fees, etc.)
    - When RAG returns insufficient information
    
    Args:
        query: Search query in natural language
        max_results: Max number of results (default: 5)
    
    Returns:
        Formatted string with search results
    """
    logger.info(f"WebSearch executing search: '{query}'")
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results, backend="html"))
        
        if not results:
            logger.warning(f"No results found for: '{query}'")
            return "No results found on the web for this query."
        
        # Format results
        formatted_results = []
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            body = result.get('body', 'No description')
            url = result.get('href', 'URL not available')
            
            formatted_results.append(
                f"[RESULT {i}]\n"
                f"Title: {title}\n"
                f"Summary: {body}\n"
                f"URL: {url}\n"
                f"---"
            )
        
        context = "\n".join(formatted_results)
        logger.info(f"WebSearch returned {len(results)} results")
        
        return context
        
    except Exception as e:
        logger.error(f"Error executing WebSearch: {e}", exc_info=True)
        return f"Error searching web: {str(e)}"
