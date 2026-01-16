"""
Semantic Chunker - Parse HTML por seções para RAG de alta qualidade

Estratégia:
- Parse por headers H2/H3 (preserva contexto semântico)
- Chunks entre 300-2000 caracteres
- Metadata enriquecida (produto, seção, pricing info)
"""

import re
from typing import List, Dict
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

# Thresholds para sizing de chunks
MIN_CHUNK_SIZE = 300
MAX_CHUNK_SIZE = 2000
OVERLAP_SIZE = 400


def parse_html_sections(html_content: bytes, source_url: str) -> List[Dict]:
    """
    Parse HTML em seções baseado em H2/H3 headers
    
    Args:
        html_content: Conteúdo HTML da página (bytes)
        source_url: URL de origem
    
    Returns:
        List de dicts com estrutura:
        {
            'content': texto da seção,
            'header': texto do header,
            'level': 'h2' ou 'h3',
            'source': URL
        }
    """
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Remover elementos não relevantes
    for element in soup(['script', 'style', 'nav', 'footer', 'header']):
        element.decompose()
    
    sections = []
    
    # Encontrar todos headers H2 e H3
    headers = soup.find_all(['h2', 'h3'])
    
    logger.debug(f"Encontrados {len(headers)} headers em {source_url}")
    
    for i, header in enumerate(headers):
        header_text = header.get_text(strip=True)
        if not header_text:
            continue
        
        # Coletar todo texto até o próximo header do mesmo nível ou superior
        content_parts = [header_text]  # Incluir header no conteúdo
        
        # Determinar onde parar (próximo header)
        next_header = None
        if i < len(headers) - 1:
            next_header = headers[i + 1]
        
        # Coletar elementos entre este header e o próximo
        current = header.find_next()
        while current:
            # Se chegou no próximo header, para
            if next_header and current == next_header:
                break
            
            # Se é um header qualquer que apareceu antes do esperado, para
            if hasattr(current, 'name') and current.name in ['h1', 'h2', 'h3'] and current != header:
                break
            
            # Coletar texto de elementos de conteúdo
            if hasattr(current, 'name') and current.name in ['p', 'div', 'li', 'ul', 'ol', 'span', 'a']:
                text = current.get_text(strip=True, separator=' ')
                if text and len(text) > 3:
                    content_parts.append(text)
            
            current = current.find_next()
        
        # Limpar e juntar conteúdo
        content = ' '.join(content_parts)
        content = re.sub(r'\s+', ' ', content).strip()
        
        if len(content) >= 50:  # Mínimo viável
            sections.append({
                'content': content,
                'header': header_text,
                'level': header.name,
                'source': source_url
            })
    
    logger.info(f"Extraídas {len(sections)} seções de {source_url}")
    return sections


def smart_chunk_sections(sections: List[Dict]) -> List[Dict]:
    """
    Ajusta tamanho dos chunks aplicando regras:
    - Chunks > MAX_CHUNK_SIZE → split com overlap
    - Chunks < MIN_CHUNK_SIZE → merge com próximo
    
    Args:
        sections: Lista de seções parseadas
    
    Returns:
        Lista de chunks ajustados
    """
    chunks = []
    i = 0
    
    while i < len(sections):
        current_section = sections[i]
        content = current_section['content']
        content_len = len(content)
        
        # Caso 1: Chunk muito grande → split
        if content_len > MAX_CHUNK_SIZE:
            logger.debug(f"Splitting large section ({content_len} chars): {current_section['header']}")
            
            # Split em pedaços com overlap
            start = 0
            while start < content_len:
                end = min(start + MAX_CHUNK_SIZE, content_len)
                chunk_text = content[start:end]
                
                chunks.append({
                    'content': chunk_text,
                    'header': current_section['header'],
                    'level': current_section['level'],
                    'source': current_section['source'],
                    'is_split': True
                })
                
                start = end - OVERLAP_SIZE if end < content_len else end
            
            i += 1
        
        # Caso 2: Chunk muito pequeno → tentar merge com próximo
        elif content_len < MIN_CHUNK_SIZE and i < len(sections) - 1:
            logger.debug(f"Merging small section ({content_len} chars): {current_section['header']}")
            
            # Merge com próximo
            next_section = sections[i + 1]
            merged_content = content + " " + next_section['content']
            
            # Se merged ainda for razoável, faz merge
            if len(merged_content) <= MAX_CHUNK_SIZE:
                chunks.append({
                    'content': merged_content,
                    'header': f"{current_section['header']} + {next_section['header']}",
                    'level': current_section['level'],
                    'source': current_section['source'],
                    'is_merged': True
                })
                i += 2  # Pula os dois
            else:
                # Senão, mantém mesmo sendo pequeno
                chunks.append(current_section)
                i += 1
        
        # Caso 3: Chunk no tamanho ideal → mantém
        else:
            chunks.append(current_section)
            i += 1
    
    logger.info(f"Chunks ajustados: {len(sections)} seções → {len(chunks)} chunks")
    return chunks


def enrich_metadata(chunk: Dict) -> Dict:
    """
    Adiciona metadata estruturada ao chunk
    
    Metadata adicionada:
    - product: nome do produto extraído da URL
    - section: texto do header da seção
    - has_pricing: bool indicando se contém info de preços
    
    Args:
        chunk: Chunk com content, header, level, source
    
    Returns:
        Chunk com metadata enriquecida
    """
    content = chunk['content']
    source = chunk['source']
    
    # Extrair nome do produto da URL
    product = "infinitepay"  # Default
    url_parts = source.rstrip('/').split('/')
    if len(url_parts) > 3:
        product = url_parts[-1] if url_parts[-1] else "home"
    
    # Detectar se contém informações de preço/taxas
    pricing_keywords = ['%', 'R$', 'taxa', 'taxas', 'grátis', 'gratuito', 'preço', 'preco']
    has_pricing = any(keyword in content.lower() for keyword in pricing_keywords)
    
    # Enriquecer metadata
    chunk['metadata'] = {
        'product': product,
        'section': chunk['header'],
        'has_pricing': has_pricing,
        'source': source,
        'header_level': chunk['level']
    }
    
    return chunk


def process_html_to_chunks(html_content: bytes, source_url: str) -> List[Dict]:
    """
    Pipeline completo: parse HTML → sizing → metadata
    
    Args:
        html_content: HTML da página
        source_url: URL de origem
    
    Returns:
        Lista de chunks prontos para embedding
    """
    # 1. Parse por seções
    sections = parse_html_sections(html_content, source_url)
    
    if not sections:
        logger.warning(f"Nenhuma seção encontrada em {source_url}")
        return []
    
    # 2. Ajustar tamanhos
    chunks = smart_chunk_sections(sections)
    
    # 3. Enriquecer metadata
    enriched_chunks = [enrich_metadata(chunk) for chunk in chunks]
    
    logger.info(
        f"Processamento completo: {source_url} → {len(enriched_chunks)} chunks"
    )
    
    return enriched_chunks

