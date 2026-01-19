"""
Output Processing Agent
Handles final text processing: language consistency, tone, and quality.
"""

from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
import logging
import re
from src.config import settings

logger = logging.getLogger(__name__)

def create_output_processor() -> Agent:
    """Creates the Output Processing Agent"""
    llm = ChatOpenAI(
        model=settings.default_model,
        temperature=0,  # CRITICAL: Zero creativity = strict instruction following
        openai_api_key=settings.openai_api_key
    )
    
    return Agent(
        role="Output Quality Specialist & Translator",
        goal="Ensure responses match the user's query language (Portuguese or English) with high quality and InfinitePay branding",
        backstory="""
        You are a professional Output Processor and Translator for InfinitePay's AI system.
        Your job is to take raw agent responses and polish them for end users.
        
        CRITICAL RESPONSIBILITY: You MUST detect the user's query language and translate the response if needed.
        
        ABOUT INFINITEPAY (use this knowledge for context and tone):
        - InfinitePay is a Brazilian fintech by CloudWalk, serving 4+ million entrepreneurs.
        - The app is 100% FREE with no monthly fees.
        - Key products:
          * InfiniteTap: Turn your phone into a card machine (NFC payments)
          * Maquininha Smart: Physical POS terminal with smart features
          * Conta Inteligente: Digital account with free Pix transfers
          * Link de Pagamento: Send payment links via WhatsApp
          * Gestão de Cobrança: Billing and invoicing tools
          * Cartão Virtual: Virtual card with 1.5% cashback
        - Value Props: Lowest fees in Brazil (up to 50% less), instant Pix, no hidden costs.
        - Target: Micro and small businesses (MEIs, autônomos, pequenas empresas).
        - Tone: Friendly, professional, empowering entrepreneurs.
        
        You DO NOT retrieve data or answer questions yourself.
        You ONLY improve existing text while preserving all facts.
        """,
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

def process_output(query: str, raw_response: str, target_language: str = None) -> str:
    """
    Process raw agent output into polished user-facing response.
    CRITICAL: Ensures response language matches query language.
    
    Args:
        query: Original user query
        raw_response: Raw response from Knowledge/Support agent
        target_language: Language detected by Router ("Portuguese" or "English")
        
    Returns:
        Polished response matching query language and InfinitePay tone
    """
    logger.info(f"Processing output for query: '{query[:50]}...'")
    
    try:
        # Use Router-detected language if available, otherwise fallback to regex
        if target_language:
            logger.info(f"🎯 [Output Processor] Using Router-detected language: {target_language}")
        else:
            # Fallback: Programmatic detection (if Router didn't provide)
            query_lower = query.lower()
            
            # Comprehensive Portuguese stopwords
            pt_stopwords = [
                'que', 'quem', 'qual', 'quais', 'quanto', 'quantos', 'onde', 'como',
                'por', 'para', 'com', 'sem', 'em', 'de', 'do', 'da', 'dos', 'das',
                'no', 'na', 'nos', 'nas', 'ao', 'aos', 'à', 'às',
                'um', 'uma', 'uns', 'umas', 'o', 'a', 'os', 'as',
                'meu', 'minha', 'meus', 'minhas', 'seu', 'sua', 'seus', 'suas',
                'é', 'são', 'está', 'estão', 'estou', 'estava', 'foram', 'foi',
                'tem', 'têm', 'tinha', 'temos', 'tenho',
                'minha', 'minhas', 'mostra', 'mostre', 'ver', 'saldo', 'transações'
            ]
            
            # Count Portuguese stopwords in query
            pt_count = sum(1 for word in pt_stopwords if f' {word} ' in f' {query_lower} ' or query_lower.startswith(f'{word} ') or query_lower.endswith(f' {word}'))
            
            # Detect language
            target_language = "Portuguese" if pt_count >= 1 else "English" # If at least 1 PT stopword, it's Portuguese
            logger.info(f"🔍 [Output Processor] Fallback detection: {target_language} (PT stopwords: {pt_count})")
        
        # STEP 2: Create ULTRA-SIMPLE, DIRECT translation task
        agent = create_output_processor()
        
        # Detect response language (simple check)
        resp_lower = raw_response.lower()
        resp_has_pt = sum(1 for w in ['seu', 'sua', 'você', 'são', 'está', 'para', 'com', 'transações'] if w in resp_lower)
        resp_has_en = sum(1 for w in ['your', 'you', 'are', 'is', 'the', 'for', 'with', 'transactions'] if w in resp_lower)
        response_language = "Portuguese" if resp_has_pt > resp_has_en else "English"
        
        logger.info(f"🔍 Response language detected: {response_language} (PT:{resp_has_pt}, EN:{resp_has_en})")
        
        # Determine if translation is needed
        needs_translation = (target_language != response_language)
        action = "TRANSLATE" if needs_translation else "IMPROVE"
        
        logger.info(f"⚙️ Action: {action} (Target: {target_language}, Response: {response_language})")
        
        task = Task(
            description=f"""
QUERY LANGUAGE: {target_language}
RESPONSE LANGUAGE: {response_language}
ACTION REQUIRED: {action}

RAW RESPONSE:
{raw_response}

INSTRUCTIONS:
{f"1. TRANSLATE the entire response from {response_language} to {target_language}" if needs_translation else "1. Keep the response in " + target_language + ", just improve quality"}
2. Remove technical IDs (happy_customer → you/você)
3. Keep all facts: numbers, dates, names intact
4. ⛔ REMOVE any "Fontes:", "Sources:", or URL lists from the text body. URLs belong in the separate sources field, NOT in the response text.

LOGIC CHECK (CRITICAL for Collaborative Queries):
- If the input contains a User Balance and a Product Price:
  - COMPARE them.
  - IF Balance >= Price: Say "Yes, you can buy it".
  - IF Balance < Price: Say "No, your balance is insufficient".
  - Cite the exact numbers (e.g. "Your balance is R$ X and the product costs R$ Y").

OUTPUT: Final text in {target_language} ONLY. No explanations, no source lists.
""",
            expected_output=f"Response in {target_language} without inline source URLs",
            agent=agent
        )
        
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True,
            memory=False,
            cache=False
        )
        
        result = crew.kickoff()
        processed_text = str(result).strip()
        
        logger.info(f"✅ Output processing complete. Target: {target_language}, Action: {action}, Length: {len(processed_text)} chars")
        return processed_text
        
    except Exception as e:
        logger.error(f"Error in Output Processor: {e}", exc_info=True)
        logger.warning("Returning raw response due to processing error")
        return raw_response
