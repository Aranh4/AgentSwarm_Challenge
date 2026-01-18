"""
Knowledge Agent - Optimized
Handles InfinitePay (RAG) and general knowledge (Web Search) queries.
Translation removed (handled by Output Processor).
"""

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from src.config import settings
from src.tools.rag_tool import rag_search_tool
from src.tools.tavily_tool import tavily_search_tool
import logging
import re

logger = logging.getLogger(__name__)

# ============================================================================
# AGENT CREATION
# ============================================================================

def create_knowledge_agent() -> Agent:
    """
    Creates a Knowledge Agent responsible for answering product inquiries
    and general knowledge questions using RAG or Web Search.
    """
    llm = ChatOpenAI(
        model=settings.default_model,
        temperature=0,  # Factual accuracy
        openai_api_key=settings.openai_api_key
    )
    
    return Agent(
        role="Knowledge Specialist",
        goal="Answer questions about InfinitePay products (via RAG) and general topics (via Web Search)",
        backstory="""You are InfinitePay's Knowledge Specialist.
        
        TOOL SELECTION RULES:
        1. For InfinitePay questions (products, fees, Tap to Pay, InfiniteTap, Phone as Machine, **Tap to Pay on Phone**):
           - TRUST RAG TOOL FIRST. The database HAS this info.
           - DO NOT use Web Search for "Tap to Pay" or "InfiniteTap features".
           - Use RAG to find the official definition and constraints.
        2. For General questions (news, current events, competitor data): Use Web Search Tool.
        3. For COMPARISONS ("better than competitors?"):
           - Use Web Search to find *specific* competitor rates (e.g. "taxas moderninha", "taxas mercado pago").
           - Do NOT simply search "compare infinitepay vs others" (too broad).
           - Compare specific numbers found.
        4. ⛔ IF USER ASKS ABOUT THEIR ACCOUNT/TRANSACTIONS/LOGIN:
           - DO NOT answer. The Support Agent will handle it.
        
        CITATION RULE:
        - You MUST list source URLs at the end: "Sources: [url1], [url2]"
        
        OUTPUT RULE:
        - Return RAW factual data.
        - BE CONCISE. Do not write long paragraphs. Bullet points are better.
        - Do NOT worry about language/tone (Output Processor handles it).""",
        tools=[rag_search_tool, tavily_search_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    return agent

# ============================================================================
# TASKS
# ============================================================================

def create_knowledge_task(agent: Agent, query: str, query_language: str = "Portuguese") -> Task:
    """
    Creates a task for the Knowledge Agent to answer a query.
    Args:
        query_language: Target language for response ("Portuguese" or "English")
    """
    return Task(
        description=f"""
Query: "{query}"

🎯 TOOL SELECTION RULES (READ CAREFULLY):

1. **InfinitePay/CloudWalk Questions** (products, services, fees):
   ✅ ALWAYS use RAG Tool FIRST (mandatory)
   ✅ MAY also use Web Search for comparisons/market context
   ❌ NEVER answer without consulting RAG

2. **General Knowledge** (news, sports, current events):
   ✅ Use Web Search Tool
   
3. **Examples**:
   - "Quais as taxas?" → RAG (must) + Web (optional for comparison)
   - "Como funciona Tap to Pay?" → RAG only
   - "Último jogo do Palmeiras?" → Web Search only
   - "InfinitePay vs PagSeguro taxas?" → RAG (InfinitePay) + Web (competitor)

📋 OUTPUT REQUIREMENTS:
- Cite sources at the end: "Sources: [url1], [url2]"
- Be concise, factual, bullet points preferred
- **CRITICAL:** Response MUST be in {query_language}. RAG content is in Portuguese - translate if needed.
""",
        expected_output=f"A helpful, accurate answer in {query_language}, citing sources.",
        agent=agent
    )

# ============================================================================
# EXECUTION FUNCTION
# ============================================================================

def run_knowledge_agent(query: str, query_language: str = "Portuguese") -> str:
    """
    Orchestrates the Knowledge Agent execution.
    Args:
        query_language: Target language for response
    """
    logger.info(f"Knowledge Agent starting (lang: {query_language}): {query}")
    
    agent = create_knowledge_agent()
    task = create_knowledge_task(agent, query, query_language=query_language)
    
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    
    result = crew.kickoff()
    return str(result)

def process_query(query: str, user_id: str = "unknown", query_language: str = "Portuguese") -> dict:
    """
    Adapter function for Router Agent compatibility.
    Args:
        query_language: Target language for response
    """
    try:
        response_text = run_knowledge_agent(query, query_language=query_language)
        
        # Extract URLs from response
        import re
        urls = re.findall(r'(https?://[^\s,\]\)]+)', response_text)
        clean_urls = [u.rstrip('.,)]') for u in urls]
        
        # Remove "Sources: ..." block from text for cleaner UI
        clean_text = response_text
        split_pattern = r'(?i)\n\s*(?:Sources|Source|Fontes|Fonte):'
        parts = re.split(split_pattern, response_text)
        
        if len(parts) > 1:
            clean_text = parts[0].strip()
        
        return {
            "response": clean_text,
            "sources": list(set(clean_urls))
        }
    except Exception as e:
        logger.error(f"Error in knowledge process_query: {e}")
        return {
            "response": f"I encountered an error searching my knowledge base: {str(e)}",
            "sources": []
        }
