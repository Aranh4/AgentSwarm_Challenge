from crewai.tools import BaseTool
import logging
import os
import requests
from src.config import settings
from pydantic import BaseModel, Field, model_validator
from typing import Type, Any, Dict

logger = logging.getLogger(__name__)

class TavilyToolInput(BaseModel):
    query: str = Field(..., description="The search query. This is the ONLY accepted argument.")

class TavilyTool(BaseTool):
    name: str = "search_web"
    description: str = """
    Searches information on the web using Tavily API.
    Input must be a JSON object with a single key 'query'.
    """
    args_schema: Type[BaseModel] = TavilyToolInput

    def _run(self, query: str) -> str:
        logger.info(f"Tavily Tool executing search: '{query}'")
        
        # Priority: Config > Env Var
        api_key = settings.tavily_api_key or os.getenv("TAVILY_API_KEY")
        
        if not api_key:
            return "Error: TAVILY_API_KEY not found in configuration or environment variables."

        try:
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": api_key,
                "query": query,
                "search_depth": "basic",
                "include_answer": True,
                "max_results": 3
            }
            
            # Timeout increased to avoid "Read timed out" on tests (Tavily can be slow)
            response = requests.post(url, json=payload, timeout=45)
            response.raise_for_status()
            data = response.json()
            
            # Format results
            results = []
            
            # Add AI answer if available
            if data.get("answer"):
                results.append(f"Direct Answer: {data['answer']}\n---")
                
            # Add search results
            for result in data.get("results", []):
                results.append(
                    f"Title: {result.get('title')}\n"
                    f"URL: {result.get('url')}\n"
                    f"Content: {result.get('content')}\n"
                    f"---"
                )
            
            final_output = "\n".join(results)
            
            from src.utils.debug_tracker import log_tool_usage
            log_tool_usage(
                tool_name="Web Search (Tavily)",
                input_str=query,
                output_str=final_output,
                metadata={"results_count": len(data.get("results", []))}
            )
                
            return final_output

        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return f"Error searching web: {str(e)}"

# Instantiate for import
tavily_search_tool = TavilyTool()
