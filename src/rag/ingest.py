"""
RAG Ingestion Pipeline

Pipeline completo:
1. Load URLs com retry
2. Semantic chunking
3. Generate embeddings (OpenAI)
4. Store in ChromaDB
5. Validate completeness
"""

import time
import requests
import chromadb
from typing import List
import logging
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from src.config import settings
from src.rag.urls import INFINITEPAY_URLS, EXPECTED_URL_COUNT
from src.rag.semantic_chunker import process_html_to_chunks

logger = logging.getLogger(__name__)


def load_url_with_retry(url: str, max_retries: int = 3, timeout: int = 30) -> bytes:
    """
    Carrega URL com retry, FALHA se não conseguir
    
    Args:
        url: URL para carregar
        max_retries: Máximo de tentativas (padrão: 3)
        timeout: Timeout em segundos (padrão: 30)
    
    Returns:
        bytes: Conteúdo HTML da página
    
    Raises:
        Exception: Se falhar após max_retries tentativas
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            logger.info(f"[OK] URL carregada: {url}")
            return response.content
        except Exception as e:
            logger.warning(f"Tentativa {attempt+1}/{max_retries} para {url}: {e}")
            if attempt == max_retries - 1:
                logger.error(f"[ERRO CRITICO] {url} nao carregou apos {max_retries} tentativas")
                raise
            time.sleep(2)  # Aguardar antes de retry


def load_infinitepay_docs() -> List[Document]:
    """
    Carrega e processa todas URLs com semantic chunking
    
    Returns:
        List[Document] - chunks prontos para embedding
    
    Raises:
        Exception: Se qualquer URL falhar
    """
    all_documents = []
    
    logger.info(f"Iniciando ingestao de {len(INFINITEPAY_URLS)} URLs...")
    
    for i, url in enumerate(INFINITEPAY_URLS, 1):
        logger.info(f"[{i}/{len(INFINITEPAY_URLS)}] Processando {url}...")
        
        try:
            # 1. Carregar HTML com retry
            html_content = load_url_with_retry(url)
            
            # 2. Processar com semantic chunker
            chunks = process_html_to_chunks(html_content, url)
            
            if not chunks:
                logger.warning(f"URL {url} nao gerou chunks!")
                continue
            
            # 3. Converter para Document objects do LangChain
            for chunk in chunks:
                doc = Document(
                    page_content=chunk['content'],
                    metadata=chunk['metadata']
                )
                all_documents.append(doc)
            
            logger.info(f"  [OK] {len(chunks)} chunks de {url}")
            
        except Exception as e:
            logger.error(f"  [FALHA] Erro ao processar {url}: {e}")
            raise  # FAIL HARD - não skip
    
    logger.info(f"[SUCESSO] Total de {len(all_documents)} chunks de {len(INFINITEPAY_URLS)} URLs")
    return all_documents


def create_chroma_client() -> chromadb.PersistentClient:
    """Cria/carrega ChromaDB persistente"""
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    logger.info(f"ChromaDB client criado: {settings.chroma_persist_dir}")
    return client


def validate_rag_completeness() -> bool:
    """
    Valida que ingestão está completa
    
    Checks:
    - ChromaDB não está vazio
    - Todas as URLs esperadas foram ingeridas
    - Cada URL tem pelo menos 1 chunk
    
    Returns:
        bool: True se validação passou
    
    Raises:
        ValueError: Se dados incompletos
        Exception: Se ChromaDB não existe
    """
    try:
        client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        collection = client.get_collection("infinitepay_docs")
    except Exception as e:
        raise ValueError(f"ChromaDB collection 'infinitepay_docs' nao existe: {e}")
    
    # Check 1: Não vazio
    total_chunks = collection.count()
    if total_chunks == 0:
        raise ValueError("[ERRO] ChromaDB vazio apos ingestao!")
    
    # Check 2: Todas URLs presentes
    all_docs = collection.get()
    unique_sources = set()
    for metadata in all_docs['metadatas']:
        if metadata and 'source' in metadata:
            unique_sources.add(metadata['source'])
    
    if len(unique_sources) < EXPECTED_URL_COUNT:
        missing = EXPECTED_URL_COUNT - len(unique_sources)
        raise ValueError(
            f"[ERRO] Ingestao incompleta! "
            f"Esperado: {EXPECTED_URL_COUNT} URLs, "
            f"Encontrado: {len(unique_sources)} URLs. "
            f"Faltam {missing} URLs."
        )
    
    logger.info(
        f"[VALIDACAO OK] {len(unique_sources)} URLs, {total_chunks} chunks"
    )
    return True


def ingest_documents() -> int:
    """
    Pipeline completo de ingestão
    
    1. Load docs (semantic chunking)
    2. Generate embeddings (OpenAI)
    3. Store in ChromaDB
    4. Validate completeness
    
    Returns:
        int: Número de chunks ingeridos
    
    Raises:
        Exception: Se falhar em carregar URLs ou validação falhar
    """
    logger.info("="*80)
    logger.info("INICIANDO INGESTAO RAG")
    logger.info("="*80)
    
    # 1. Load documents
    logger.info("Etapa 1: Carregando documentos...")
    documents = load_infinitepay_docs()
    
    if not documents:
        raise ValueError("Nenhum documento foi carregado!")
    
    logger.info(f"[OK] {len(documents)} documentos carregados")
    
    # 2. Setup embeddings
    logger.info("Etapa 2: Configurando embeddings OpenAI...")
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=settings.openai_api_key
    )
    logger.info("[OK] Embeddings configurados")
    
    # 3. Create/load Chroma vectorstore
    logger.info("Etapa 3: Criando ChromaDB vectorstore...")
    
    # Deletar collection existente se houver (fresh start)
    client = create_chroma_client()
    try:
        client.delete_collection("infinitepay_docs")
        logger.info("[OK] Collection antiga deletada")
    except:
        pass
    
    # Criar nova collection e adicionar documentos
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="infinitepay_docs",
        persist_directory=settings.chroma_persist_dir
    )
    
    logger.info(f"[OK] ChromaDB populado com {len(documents)} chunks")
    
    # 4. Validação obrigatória
    logger.info("Etapa 4: Validando completeness...")
    validate_rag_completeness()
    
    logger.info("="*80)
    logger.info(f"INGESTAO COMPLETA: {len(documents)} chunks")
    logger.info("="*80)
    
    return len(documents)

