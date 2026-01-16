import logging
import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain.tools import tool

from src.config import settings
from src.tools.rag_tool import rag_search_tool
from src.tools.tavily_tool import tavily_search_tool

logger = logging.getLogger(__name__)

# ============================================================================
# AGENT DEFINITION
# ============================================================================

from datetime import datetime

def create_knowledge_agent() -> Agent:
    """
    Creates the Knowledge Agent specialized in RAG and Web Search.
    Now uses Tavily for better web search results.
    """
    llm = ChatOpenAI(
        model=settings.default_model,
        api_key=settings.openai_api_key,
        temperature=0.1
    )
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    agent = Agent(
        role='Knowledge Specialist',
        goal=f'Provide accurate information about InfinitePay products and general knowledge. Today is {current_date}.',
        backstory=f"""You are a Data Retrieval Specialist for InfinitePay.
        Your ONLY job is to find accurate information using your tools.
        
        Current Date: {current_date}. You are aware of the current year and date.
        
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
        - Return RAW factual data. Do NOT worry about language, tone, or formatting.
        - Just focus on accuracy and completeness of information.""",
        tools=[rag_search_tool, tavily_search_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    return agent

# ============================================================================
# TASKS
# ============================================================================

def create_knowledge_task(agent: Agent, query: str) -> Task:
    """
    Creates a task for the Knowledge Agent to answer a query.
    """
    return Task(
        description=f"""
        Answer the following query using your tools (RAG or Web Search).
        Query: {query}
        
        If it's about InfinitePay, use RAG.
        If it's about general knowledge/news, use Web Search.
        MATCH THE USER'S LANGUAGE.
        """,
        expected_output="A helpful, accurate answer based on the retrieved information, citing sources.",
        agent=agent
    )

# ============================================================================
# EXECUTION FUNCTION
# ============================================================================

def run_knowledge_agent(query: str) -> str:
    """
    Orchestrates the Knowledge Agent execution.
    """
    logger.info(f"Knowledge Agent starting for query: {query}")
    
    agent = create_knowledge_agent()
    task = create_knowledge_task(agent, query)
    
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    
    result = crew.kickoff()
    return str(result)

def process_query(query: str, user_id: str = "unknown") -> dict:
    """
    Adapter function for Router Agent compatibility.
    """
    try:
        response_text = run_knowledge_agent(query)
        
        # --- TRANSLATION LAYER (ROBUSTNESS) ---
        # Ensure response matches query language regardless of RAG context
        final_text = response_text
        try:
            translation_llm = ChatOpenAI(
                model=settings.default_model,
                api_key=settings.openai_api_key,
                temperature=0.0
            )
            
            # Regex to detect Portuguese (stopwords/question words)
            pt_pattern = r'\b(que|quem|qual|quais|quanto|quantos|onde|como|por|para|com|em|um|uma|os|as|ao|dos|das|é|são)\b'
            is_pt = bool(re.search(pt_pattern, query.lower()))
            target_lang = "Portuguese" if is_pt else "English"
            
            prompt = f"""
            Task: REWRITE the "Agent Response" to match the language of the "User Query".
            
            User Query: "{query}"
            Agent Response: "{response_text}"
            
            Instructions:
            1. Identify the language of the User Query (English or Portuguese).
            2. REWRITE the Agent Response in that SAME language.
            3. PRESERVE strict proper nouns (InfinitePay, Maquininha Smart, Confere).
            4. TRANSLATE all normal words (e.g., "taxas" -> "fees", "custa" -> "costs", "maquininha" -> "machine" if generic).
            
            OUTPUT ONLY THE REWRITTEN TEXT.
            """
            
            result = translation_llm.invoke(prompt)
            if result and result.content:
                final_text = result.content.strip()
                
        except Exception as t_err:
            logger.warning(f"Translation layer failed: {t_err}")
            final_text = response_text
        
        response_text = final_text
        # ----------------------------------------
        
        # Extract URLs
        import re
        # Capture URLs, excluding common trailing punctuation
        # pattern matches http/https followed by non-whitespace, stopping at punctuation often used as delimiters
        urls = re.findall(r'(https?://[^\s,\]\)]+)', response_text)
        
        # Clean specific trailing characters just in case
        clean_urls = [u.rstrip('.,)]') for u in urls]
        
        # Remove "Sources: ..." block from text for cleaner UI
        # We look for "Sources:" or "Source:" or "Fontes:" at the start of a line (case insensitive)
        clean_text = response_text
        split_pattern = r'(?i)\n\s*(?:Sources|Source|Fontes|Fonte):'
        parts = re.split(split_pattern, response_text)
        
        if len(parts) > 1:
            # Take everything before the sources block
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
