"""
Router Agent - Swarm Orchestrator
Uses LLM with few-shot examples for intelligent query routing.
"""

from langchain_openai import ChatOpenAI
import logging
from typing import Literal, Dict, List

from src.config import settings
from src.agents.knowledge_agent import process_query as knowledge_process
from src.agents.support_agent import process_support_query as support_process
from src.agents.output_processor import process_output
import json

logger = logging.getLogger(__name__)

QueryType = Literal["KNOWLEDGE", "SUPPORT", "BOTH"]


class RouterAgent:
    """
    Routes queries to appropriate agents using LLM intelligence.
    """
    
    # Few-shot prompt with explicit examples
    CLASSIFICATION_PROMPT = """Classify this query. Reply with ONE word only.

Examples:
Q: "What are the fees for the Smart machine?" → KNOWLEDGE
Q: "How does Pix work?" → KNOWLEDGE
Q: "Latest Palmeiras news" → KNOWLEDGE
Q: "Why is my account blocked?" → SUPPORT
Q: "My transfer failed" → SUPPORT
Q: "What is my balance?" → SUPPORT
Q: "What are the fees and why is my account blocked?" → BOTH

Rules:
- KNOWLEDGE = questions about products, services, general info
- SUPPORT = questions about USER's personal data (account, balance, transactions)
- BOTH = mix of both types

Q: "{query}" →"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.default_model,
            temperature=0.0,
            openai_api_key=settings.openai_api_key
        )
    
    def classify_query(self, query: str) -> QueryType:
        """Classify query using LLM with few-shot examples."""
        try:
            prompt = self.CLASSIFICATION_PROMPT.format(query=query)
            response = self.llm.invoke(prompt)
            result = response.content.strip().upper()
            
            # Extract just the classification word
            for valid in ["KNOWLEDGE", "SUPPORT", "BOTH"]:
                if valid in result:
                    logger.info(f"[Router] Classified as: {valid}")
                    return valid
            
            logger.warning(f"[Router] Unexpected: '{result}', defaulting to KNOWLEDGE")
            return "KNOWLEDGE"
            
        except Exception as e:
            logger.error(f"[Router] Error: {e}")
            return "KNOWLEDGE"
    
    def route_and_execute(self, query: str, user_id: str) -> Dict:
        """Route to appropriate agent(s) and aggregate responses."""
        query_type = self.classify_query(query)
        
        responses = []
        agents_used = []
        all_sources = []
        
        try:
            if query_type in ["KNOWLEDGE", "BOTH"]:
                logger.info("[Router] → Knowledge Agent")
                result = knowledge_process(query, user_id)
                responses.append(("Produtos/Serviços", result))
                agents_used.append("knowledge")
                all_sources.extend(result.get("sources", []))
            
            if query_type in ["SUPPORT", "BOTH"]:
                logger.info("[Router] → Support Agent")
                result = support_process(query, user_id)
                responses.append(("Sua Conta", result))
                agents_used.append("support")
                all_sources.extend(result.get("sources", []))
            
            # Build final response (raw agent output)
            if len(responses) == 1:
                raw_final_response = responses[0][1]["response"]
            else:
                parts = [f"**{name}:**\n{r['response']}" for name, r in responses]
                raw_final_response = "\n\n---\n\n".join(parts)
            
            # Process output through Output Processing Agent
            logger.info("[Router] → Output Processing Agent")
            polished_response = process_output(query, raw_final_response)
            
            return {
                "response": polished_response,
                "agent_used": "+".join(agents_used),
                "sources": list(set(all_sources)),
                "routing": query_type
            }
            
        except Exception as e:
            logger.error(f"[Router] Execution error: {e}", exc_info=True)
            return {
                "response": f"Erro: {str(e)}",
                "agent_used": "error",
                "sources": [],
                "error": str(e)
            }


# Singleton
router_agent = RouterAgent()

def route_query(query: str, user_id: str) -> Dict:
    """Public function to route queries through the swarm."""
    return router_agent.route_and_execute(query, user_id)
