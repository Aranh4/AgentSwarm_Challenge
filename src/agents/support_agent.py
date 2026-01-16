"""
Customer Support Agent
Handles transactional queries and user account issues.
"""

from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
import logging
import re
from src.config import settings
from src.tools.support_tools import get_user_info_tool, get_user_transactions_tool, get_user_cards_tool

logger = logging.getLogger(__name__)

SUPPORT_AGENT_ROLE = "Customer Support Specialist"
SUPPORT_AGENT_GOAL = """
Solve user problems efficiently by checking their account data.
Verify WHY something happened (failed transaction, blocked account) and explain clearly to the user.
"""

SUPPORT_AGENT_BACKSTORY = """
You are a Data Retrieval Specialist for InfinitePay's customer support system.
You have direct access to the user's account database.

Your ONLY job is to:
1. SECURITY: Always verify if the user exists (use get_user_info first).
2. RETRIEVE: Get relevant data using available tools.
3. DIAGNOSE: Explain WHY something happened based on the data.

You can check balances, transaction history, and card limits.

IMPORTANT: Return RAW diagnostic data. Do NOT worry about language, tone, or being empathetic.
Just focus on accurate diagnosis based on database facts.
"""

def create_support_agent() -> Agent:
    """Creates the Customer Support Agent"""
    llm = ChatOpenAI(
        model=settings.default_model,
        temperature=0.0, # Zero temp for factual data handling
        openai_api_key=settings.openai_api_key
    )
    
    return Agent(
        role=SUPPORT_AGENT_ROLE,
        goal=SUPPORT_AGENT_GOAL,
        backstory=SUPPORT_AGENT_BACKSTORY,
        tools=[get_user_info_tool, get_user_transactions_tool, get_user_cards_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

def process_support_query(query: str, user_id: str) -> dict:
    """
    Process a support query for a specific user.
    """
    logger.info(f"Support Agent processing for {user_id}: '{query}'")
    
    try:
        agent = create_support_agent()
        
        task = Task(
            description=f"""
USER (ID: {user_id}): "{query}"

INSTRUCTIONS:
1. Use 'get_user_info' to check account status and balance.
2. IF needed, use 'get_user_transactions' or 'get_user_cards' to investigate details.
3. Diagnose the problem based on the data.
4. Return diagnostic information in plain text (language doesn't matter).

Example Diagnosis:
- If user asks why transfer failed → Check last transactions → See 'failed' status and 'reason' → Return that reason.

IMPORTANT:
- If User ID is not found, state you cannot access the account.
- Do not make up data. Use only what tools return.
- Include all relevant details (balance, transaction status, dates, amounts).
""",
            expected_output="Direct answer explaining the situation based on DB data.",
            agent=agent
        )
        
        crew = Crew(
            agents=[agent], 
            tasks=[task], 
            verbose=True,
            memory=False, # Disable memory to prevent context leak between requests
            cache=False   # Disable caching to force tool re-execution
        )
        result = crew.kickoff()
        
        return {
            "response": str(result),
            "agent": "support",
            "sources": ["Internal Database"], # Symbolic source
            "raw_output": result
        }
        
    except Exception as e:
        logger.error(f"Error in Support Agent: {e}", exc_info=True)
        return {
            "response": f"System Error: {str(e)}",
            "agent": "support",
            "sources": [],
            "error": str(e)
        }
