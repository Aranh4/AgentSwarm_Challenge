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

OBJECTIVE: Gather user financial data to answer the query.

MANDATORY ACTIONS:
1. EXECUTE tool `get_user_info` to get the CURRENT BALANCE and status. (CRITICAL)
2. EXECUTE tool `get_user_transactions` IF the query mentions history/spending.

OUTPUT GUIDELINES:
- You MUST report the exact numbers found in the tool output.
- If you cannot run the tool, say "TOOL_FAILURE".
- Do NOT guess the balance.
""",
                expected_output="Raw data summary including: Balance, Status, Recent Transactions (if relevant).",
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
        
        # Capture current tracker instance manually
        from src.utils.debug_tracker import get_tracker_instance, set_tracker_instance
        current_tracker = get_tracker_instance()

        # Wrappers to set the tracker in the new thread
        def run_support_safe():
            if current_tracker:
                set_tracker_instance(current_tracker)
            return run_support()

        def run_knowledge_safe():
            if current_tracker:
                set_tracker_instance(current_tracker)
            return run_knowledge()
        
        # Run both in parallel using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            support_future = executor.submit(run_support_safe)
            knowledge_future = executor.submit(run_knowledge_safe)
            
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
