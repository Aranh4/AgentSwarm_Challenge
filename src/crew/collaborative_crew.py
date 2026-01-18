"""
Optimized Collaborative Crew - Parallel Execution
Support + Knowledge run concurrently, Output Processor synthesizes.
"""

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from src.config import settings
from src.agents.support_agent import create_support_agent as create_base_support_agent
from src.tools.rag_tool import rag_search_tool
from src.tools.tavily_tool import tavily_search_tool
from src.agents.knowledge_agent import create_knowledge_agent, create_knowledge_task
from src.agents.output_processor import process_output
import logging
import re
import concurrent.futures

logger = logging.getLogger(__name__)

def create_support_agent():
    """Creates Support Agent for user context gathering"""
    # Use the existing support agent creation but modify backstory
    agent = create_base_support_agent()
    
    # Override backstory to emphasize selective tool usage
    agent.backstory = """You are a support analyst specializing in user account diagnostics.
        Your job is to gather relevant user information efficiently.
        
        TOOL USAGE GUIDELINES:
        - get_user_info: Check account status, balance, plan. ALWAYS use for any user query.
        - get_user_transactions: Use ONLY if query mentions: payments, transfers, transactions, purchases, history.
        - get_user_cards: Use ONLY if query mentions: card, cartão, limit, spending.
        
        DO NOT use all tools blindly. Be selective based on the query."""
    
    return agent


def run_collaborative_query(query: str, user_id: str, query_language: str = "Portuguese") -> dict:
    """
    Execute parallel Support + Knowledge, then synthesize with Output Processor.
    
    Improvements:
    - Support and Knowledge run concurrently (not sequential)
    - Support only uses necessary tools (not all tools forcefully)
    - Single translation via Output Processor
    """
    logger.info(f"[CollaborativeCrew] Parallel execution for user={user_id}")
    
    try:
        support_result = None
        knowledge_result = None
        knowledge_sources = []
        
        # Define parallel execution functions
        def run_support():
            """Gather user context"""
            agent = create_support_agent()
            task = Task(
                description=f"""
User ID: {user_id}
Query: "{query}"

Gather relevant user context:
1. ALWAYS use get_user_info (account status is critical)
2. Use get_user_transactions ONLY if query mentions payments/transfers/history
3. Use get_user_cards ONLY if query mentions cards/limits

Return a concise summary of findings.
""",
                expected_output="Concise user profile with relevant data only",
                agent=agent
            )
            crew = Crew(agents=[agent], tasks=[task], verbose=False)
            return str(crew.kickoff())
        
        def run_knowledge():
            """Answer product/service question"""
            agent = create_knowledge_agent()
            task = create_knowledge_task(agent, query)
            crew = Crew(agents=[agent], tasks=[task], verbose=False)
            result = str(crew.kickoff())
            
            # Extract sources from knowledge response
            urls = re.findall(r'(https?://[^\s,\]\)]+)', result)
            clean_urls = [u.rstrip('.,)]') for u in urls]
            
            return result, list(set(clean_urls))
        
        # Run both in parallel using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            support_future = executor.submit(run_support)
            knowledge_future = executor.submit(run_knowledge)
            
            support_result = support_future.result()
            knowledge_result, knowledge_sources = knowledge_future.result()
        
        logger.info("[CollaborativeCrew] Both agents completed. Synthesizing...")
        
        # Combine results for Output Processor
        combined = f"""
User Context:
{support_result}

Product/Service Information:
{knowledge_result}

Original Query: {query}
"""
        
        # Let Output Processor synthesize and translate
        final_response = process_output(query, combined)
        
        return {
            "response": final_response,
            "agent_used": ["support", "knowledge"],
            "sources": knowledge_sources
        }
        
    except Exception as e:
        logger.error(f"[CollaborativeCrew] Error: {e}", exc_info=True)
        return {
            "response": f"I encountered an error processing your request: {str(e)}",
            "agent_used": ["error"],
            "sources": []
        }
