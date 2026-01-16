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
        temperature=0.3,  # Allow some creativity for text improvement
        openai_api_key=settings.openai_api_key
    )
    
    return Agent(
        role="Output Quality Specialist",
        goal="Ensure responses are in the correct language, high quality, and InfinitePay-branded",
        backstory="""
        You are a professional Output Processor for InfinitePay's AI system.
        Your job is to take raw agent responses and polish them for end users.
        
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

def process_output(query: str, raw_response: str) -> str:
    """
    Process raw agent output into polished user-facing response.
    
    Args:
        query: Original user query
        raw_response: Raw response from Knowledge/Support agent
        
    Returns:
        Polished response matching query language and InfinitePay tone
    """
    logger.info(f"Processing output for query: '{query[:50]}...'")
    
    try:
        # Detect target language using regex
        pt_pattern = r'\b(que|quem|qual|quais|quanto|quantos|onde|como|por|para|com|em|um|uma|os|as|ao|dos|das|é|são|minha|meu|está|estão)\b'
        is_pt = bool(re.search(pt_pattern, query.lower()))
        target_lang = "Portuguese" if is_pt else "English"
        
        logger.info(f"Detected target language: {target_lang}")
        
        # Create processing task
        agent = create_output_processor()
        
        task = Task(
            description=f"""
Process this agent response for a user.

USER QUERY (for context): "{query}"
RAW AGENT RESPONSE: "{raw_response}"

TARGET LANGUAGE: {target_lang}

YOUR TASK:
1. REWRITE the response in {target_lang}
2. Improve text quality:
   - Fix grammar and spelling
   - Make it clear and concise
   - Use professional but friendly tone
   - Remove redundancies
7. PRESERVE exactly:
   - All factual data (numbers, dates, names)
   - Brand terms: InfinitePay, InfiniteSmart, InfiniteTap, Confere
   - Technical terms: Pix, débito, crédito, taxa, etc. (Keep these in Portuguese if they are proper nouns/concepts)
   - Currency values: R$, %, digits

8. TRANSLATIONS (Important):
   - "Maquininha Smart" (in English) -> "Smart POS" or "Card Machine"
   - but keep "InfinitePay" as is.

9. AGGRESSIVE TRANSLATION OF KEYS:
   - You MUST translate these specific keys if found:
     - "Date:" -> "Data:" (PT)
     - "Type:" -> "Tipo:" (PT)
     - "Amount:" -> "Valor:" (PT)
     - "Status:" -> "Status:" (PT)
   - Do NOT leave "Date" or "Type" in English when output is Portuguese.

10. CLEANUP CONTRADICTIONS:
    - If the response contains helpful data BUT ALSO says "I cannot help" or "I am unable to assist", REMOVE the negative refusal.
    - Keep the helpful data only.

11. If response contains "Sources:", keep it at the end

OUTPUT ONLY THE FINAL PROCESSED TEXT. NO EXPLANATIONS OR META-COMMENTS.
""",
            expected_output=f"Polished response in {target_lang}, preserving all facts",
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
        
        logger.info(f"Processing complete. Output length: {len(processed_text)} chars")
        return processed_text
        
    except Exception as e:
        logger.error(f"Error in Output Processor: {e}", exc_info=True)
        # Fallback: return original response if processing fails
        logger.warning("Returning raw response due to processing error")
        return raw_response
