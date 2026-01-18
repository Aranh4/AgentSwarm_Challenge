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
    
    # Few-shot prompt with explicit examples (includes language detection)
    CLASSIFICATION_PROMPT = """Classify query. Return TWO words separated by pipe: ROUTING|LANGUAGE

Examples:
"Fees for Smart?" -> KNOWLEDGE|English
"Quais são as taxas?" -> KNOWLEDGE|Portuguese
"Pix working?" -> KNOWLEDGE|English
"Como funciona o Pix?" -> KNOWLEDGE|Portuguese
"Palmeiras news" -> KNOWLEDGE|English
"Notícias do Palmeiras" -> KNOWLEDGE|Portuguese
"Account blocked?" -> SUPPORT|English
"Minha conta está bloqueada?" -> SUPPORT|Portuguese
"Transfer failed" -> SUPPORT|English
"Transferência falhou" -> SUPPORT|Portuguese
"My balance?" -> SUPPORT|English
"Qual meu saldo?" -> SUPPORT|Portuguese
"My transactions" -> SUPPORT|English
"Minhas transações" -> SUPPORT|Portuguese
"Show my transfers" -> SUPPORT|English
"Mostre minhas transferências" -> SUPPORT|Portuguese
"Last payments" -> SUPPORT|English
"Últimos pagamentos" -> SUPPORT|Portuguese
"My cards" -> SUPPORT|English
"Meus cartões" -> SUPPORT|Portuguese
"Fees and blocked account?" -> BOTH|English
"Taxas e conta bloqueada?" -> BOTH|Portuguese
"Best product for me?" -> BOTH|English
"Qual o melhor produto pra mim?" -> BOTH|Portuguese
"Can I afford Smart?" -> BOTH|English
"Posso comprar a Smart?" -> BOTH|Portuguese

Rules:
- SUPPORT: Queries about user's OWN data (balance, transactions, transfers, cards, account status)
- KNOWLEDGE: General product info, fees, features, news, how things work
- BOTH: Only when user asks for PERSONALIZED recommendation combining their data + product info
- LANGUAGE: Portuguese or English (based on query words, NOT mentioned brands)

Query: "{query}" ->"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.default_model,
            temperature=0.0,
            openai_api_key=settings.openai_api_key
        )
    
    def classify_query(self, query: str) -> tuple[QueryType, str]:
        """Classify query using LLM with few-shot examples.
        
        Returns:
            tuple: (routing_type, language) e.g. ("KNOWLEDGE", "English")
        """
        try:
            prompt = self.CLASSIFICATION_PROMPT.format(query=query)
            response = self.llm.invoke(prompt)
            result = response.content.strip().upper()
            
            # Parse "ROUTING|LANGUAGE" format
            if "|" in result:
                parts = result.split("|")
                routing = parts[0].strip()
                language = parts[1].strip().capitalize()  # "ENGLISH" -> "English"
            else:
                # Fallback: old format (just routing)
                routing = result
                language = "Portuguese"  # Default
            
            # Validate routing
            valid_routing = None
            for valid in ["KNOWLEDGE", "SUPPORT", "BOTH"]:
                if valid in routing:
                    valid_routing = valid
                    break
            
            if not valid_routing:
                logger.warning(f"[Router] Unexpected routing: '{routing}', defaulting to BOTH")
                valid_routing = "BOTH"
            
            # Validate language
            if "ENGLISH" in language.upper() or "EN" in language.upper():
                detected_lang = "English"
            elif "PORTUGUESE" in language.upper() or "PT" in language.upper() or "PORTUGUES" in language.upper():
                detected_lang = "Portuguese"
            else:
                detected_lang = "Portuguese"  # Default
            
            from src.utils.debug_tracker import set_routing_info
            set_routing_info(valid_routing, detected_lang)

            logger.info(f"[Router] Classified as: {valid_routing} | Language: {detected_lang}")
            return (valid_routing, detected_lang)
            
        except Exception as e:
            logger.error(f"[Router] Error: {e}, defaulting to BOTH|Portuguese")
            return ("BOTH", "Portuguese")
    
    def route_and_execute(self, query: str, user_id: str) -> Dict:
        """Route to appropriate agent(s) and aggregate responses.
        
        Hybrid approach:
        - BOTH: Uses collaborative crew with context sharing between agents
        - Single agent: Uses direct function calls for better performance
        """
        # Get routing and language from LLM in single call
        query_type, query_language = self.classify_query(query)
        logger.info(f"🎯 [Router] Routing: {query_type} | Language: {query_language}")
        
        try:
            # BOTH queries: Use collaborative crew for true context sharing
            if query_type == "BOTH":
                logger.info(f"[Router] → Collaborative Crew (lang: {query_language})")
                from src.crew.collaborative_crew import run_collaborative_query
                return run_collaborative_query(query, user_id, query_language=query_language)
            
            # Single agent queries: Direct function calls (faster)
            if query_type == "KNOWLEDGE":
                logger.info(f"[Router] → Knowledge Agent (lang: {query_language})")
                result = knowledge_process(query, user_id, query_language=query_language)
                raw_response = result["response"]
                sources = result.get("sources", [])
                agents_used = ["knowledge"]
            else:  # SUPPORT
                logger.info(f"[Router] → Support Agent (lang: {query_language})")
                result = support_process(query, user_id, query_language=query_language)
                raw_response = result["response"]
                sources = result.get("sources", [])
                agents_used = ["support"]
            
            # Process output through Output Processing Agent
            logger.info(f"[Router] → Output Processing Agent (target lang: {query_language})")
            polished_response = process_output(query, raw_response, target_language=query_language)
            
            return {
                "response": polished_response,
                "agent_used": agents_used,
                "sources": sources,
                "routing": query_type
            }
            
        except Exception as e:
            logger.error(f"[Router] Execution error: {e}", exc_info=True)
            return {
                "response": f"Erro: {str(e)}",
                "agent_used": ["error"],
                "sources": [],
                "error": str(e)
            }


# Singleton
router_agent = RouterAgent()

def route_query(query: str, user_id: str) -> Dict:
    """Public function to route queries through the swarm."""
    return router_agent.route_and_execute(query, user_id)
