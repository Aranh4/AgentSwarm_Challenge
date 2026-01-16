# CloudWalk Agent Swarm 🤖

> Sistema multi-agente inteligente para suporte ao cliente e base de conhecimento da **InfinitePay**.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.121+-purple.svg)](https://docs.crewai.com/)

---

## 📋 Índice

1. [Visão Geral](#-visão-geral)
2. [Arquitetura do Sistema](#-arquitetura-do-sistema)
3. [Agentes Implementados](#-agentes-implementados)
4. [RAG Pipeline](#-rag-pipeline)
5. [Como Executar](#-como-executar)
6. [API Endpoints](#-api-endpoints)
7. [Testes](#-testes)
8. [Decisões de Design](#-decisões-de-design)
9. [Uso de LLMs no Desenvolvimento](#-uso-de-llms-no-desenvolvimento)

---

## 🎯 Visão Geral

Este projeto implementa um **Agent Swarm** (enxame de agentes) que processa mensagens de usuários através de múltiplos agentes especializados colaborando entre si:

| Agente | Responsabilidade |
|--------|------------------|
| **Router Agent** | Analisa a intenção e roteia para o agente correto |
| **Knowledge Agent** | Responde perguntas usando RAG (InfinitePay) ou Web Search |
| **Support Agent** | Consulta dados do cliente (transações, status, etc.) |
| **Output Processor** | Garante qualidade e consistência de linguagem |

### Funcionalidades Principais

- ✅ **RAG Pipeline** com 18 URLs da InfinitePay indexadas
- ✅ **Web Search** para perguntas gerais (Tavily)
- ✅ **Suporte ao Cliente** com banco SQLite mock
- ✅ **Colaboração Multi-Agent** para perguntas complexas
- ✅ **Frontend** moderno com tema InfinitePay
- ✅ **Docker** pronto para deploy

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                      User Request                           │
│              POST /chat {"message", "user_id"}              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
│                    (Validation, CORS, Logging)               │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │     ROUTER AGENT       │
              │  Classifica a query:   │
              │  • knowledge           │
              │  • support             │
              │  • knowledge+support   │
              └───────────┬────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────────┐
│   KNOWLEDGE   │ │    SUPPORT    │ │  KNOWLEDGE+SUPPORT│
│     AGENT     │ │     AGENT     │ │   (Collaborative) │
│               │ │               │ │                   │
│ Tools:        │ │ Tools:        │ │ Context Sharing   │
│ • RAG Search  │ │ • get_user    │ │ entre Tasks       │
│ • Web Search  │ │ • get_txns    │ │                   │
└───────┬───────┘ └───────┬───────┘ └─────────┬─────────┘
        │                 │                   │
        └─────────────────┴───────────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │   OUTPUT PROCESSOR     │
              │  • Tradução automática │
              │  • Consistência de tom │
              │  • Qualidade do texto  │
              └───────────┬────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  JSON Response  │
                 │  • response     │
                 │  • agent_used   │
                 │  • sources      │
                 └─────────────────┘
```

### Fluxo de Dados

1. **Request** chega via POST `/chat`
2. **Router Agent** classifica a intenção usando LLM
3. **Agente(s) especializado(s)** são acionados:
   - Knowledge: busca no RAG ou web
   - Support: consulta banco de dados do cliente
   - Ambos: contexto compartilhado entre tasks
4. **Output Processor** polui a resposta final
5. **Response** retornada com metadados (agente usado, fontes)

---

## 🤖 Agentes Implementados

### Router Agent (`src/agents/router_agent.py`)

- **Função:** Ponto de entrada para todas as mensagens
- **Decisão:** Classifica queries em categorias
- **Output:** JSON com `routing` e `agents_needed`

### Knowledge Agent (`src/agents/knowledge_agent.py`)

- **Função:** Responde perguntas sobre InfinitePay e perguntas gerais
- **Tools:**
  - `search_infinitepay_knowledge` - Busca no RAG (ChromaDB)
  - `search_web` - Busca na internet (Tavily)
- **Prioridade:** RAG first para perguntas sobre produtos InfinitePay

### Support Agent (`src/agents/support_agent.py`)

- **Função:** Suporte ao cliente com dados do usuário
- **Tools:**
  - `get_user_account_data` - Dados da conta
  - `get_user_transactions` - Histórico de transações
  - `get_user_cards` - Cartões vinculados
- **Database:** SQLite com dados mock

### Output Processor (`src/agents/output_processor.py`)

- **Função:** Pós-processamento de qualidade
- **Responsabilidades:**
  - Detectar idioma da query e traduzir resposta
  - Manter tom profissional InfinitePay
  - Traduzir headers de dados estruturados
  - Remover mensagens contraditórias

---

## 📚 RAG Pipeline

### Arquitetura RAG

```
┌─────────────────────────────────────────────────────────────┐
│                        INGESTÃO                              │
│                                                              │
│  18 URLs InfinitePay  →  Scraping HTML  →  Semantic Chunks   │
│         ↓                     ↓                   ↓          │
│   requests + retry      BeautifulSoup      ~500 chars/chunk  │
│                                                              │
│  Chunks  →  OpenAI Embeddings  →  ChromaDB (Persistent)      │
│                text-embedding-3-small                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        RETRIEVAL                             │
│                                                              │
│  User Query  →  Embedding  →  Similarity Search  →  Top 5   │
│       ↓             ↓              ↓                  ↓      │
│   "Taxas da     Vector        ChromaDB          Chunks mais  │
│   maquininha"   [0.12, ...]    cosine            relevantes  │
│                                                              │
│  Chunks  →  LLM Context  →  Generated Response              │
└─────────────────────────────────────────────────────────────┘
```

### URLs Indexadas (18 páginas)

- `infinitepay.io` (home)
- `infinitepay.io/taxas` ⭐ (taxas detalhadas)
- `infinitepay.io/maquininha`
- `infinitepay.io/maquininha-celular`
- `infinitepay.io/tap-to-pay`
- `infinitepay.io/pdv`
- `infinitepay.io/receba-na-hora`
- `infinitepay.io/gestao-de-cobranca`
- `infinitepay.io/link-de-pagamento`
- `infinitepay.io/loja-online`
- `infinitepay.io/boleto`
- `infinitepay.io/conta-digital`
- `infinitepay.io/pix`
- `infinitepay.io/pix-parcelado`
- `infinitepay.io/emprestimo`
- `infinitepay.io/cartao`
- `infinitepay.io/rendimento`

### Código Principal

- `src/rag/ingest.py` - Pipeline de ingestão
- `src/rag/search.py` - Interface de busca
- `src/rag/urls.py` - Lista de URLs
- `src/rag/semantic_chunker.py` - Chunking inteligente

---

## 🚀 Como Executar

### Pré-requisitos

- Python 3.11+
- OpenAI API Key
- (Opcional) Tavily API Key para web search

### Opção 1: Docker (Recomendado)

```bash
# 1. Clonar repositório
git clone <repo-url>
cd cloudwalk-agent-swarm

# 2. Criar arquivo .env
cp .env.example .env
# Edite .env e adicione sua OPENAI_API_KEY

# 3. Subir container
docker-compose up --build

# 4. Acessar
# Frontend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Opção 2: Local (Desenvolvimento)

```bash
# 1. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar .env
cp .env.example .env
# Adicione OPENAI_API_KEY

# 4. Ingerir dados RAG (primeira vez)
python scripts/ingest_rag.py

# 5. Executar servidor
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Variáveis de Ambiente (.env)

```env
OPENAI_API_KEY=sk-...           # Obrigatório
TAVILY_API_KEY=tvly-...         # Opcional (web search)
ENVIRONMENT=development
LOG_LEVEL=INFO
```

---

## 📡 API Endpoints

### POST /chat

Envia mensagem para o Agent Swarm.

**Request:**
```json
{
  "message": "Quais as taxas da maquininha smart?",
  "user_id": "client789"
}
```

**Response:**
```json
{
  "response": "A Maquininha Smart da InfinitePay tem taxas a partir de 0,75%...",
  "agent_used": "knowledge",
  "sources": ["https://www.infinitepay.io/taxas"]
}
```

### GET /health

Verifica status da API.

**Response:**
```json
{
  "status": "healthy",
  "environment": "development",
  "service": "CloudWalk Agent Swarm"
}
```

### Swagger UI

Acesse `http://localhost:8000/docs` para documentação interativa.

---

## 🧪 Testes

### Executar Testes

```bash
# Todos os testes
pytest tests/ -v

# Testes específicos
pytest tests/test_rag.py -v
pytest tests/test_api.py -v

# Com cobertura
pytest tests/ --cov=src --cov-report=html
```

### Scripts de Validação

```bash
# Smoke test rápido
python scripts/smoke_test.py

# Relatório completo de testes
python scripts/generate_test_report.py

# Verificar fixes específicos
python scripts/verify_fixes.py
```

### Estratégia de Testes

1. **Unit Tests:** Funções isoladas (RAG search, tools)
2. **Integration Tests:** Fluxo completo de agentes
3. **E2E Tests:** Cenários reais via API

---

## 🎨 Decisões de Design

### Por que CrewAI?

- Framework especializado em orquestração de agentes
- Suporte nativo a context sharing entre tasks
- Integração simples com LangChain
- Código mais limpo que implementações manuais

### Por que ChromaDB?

- Vector store local (sem dependências externas)
- Fácil de dockerizar
- Persistência em disco
- API simples e eficiente

### Por que Tavily (Web Search)?

- Resultados estruturados para LLMs
- API confiável e rápida
- Fallback para DuckDuckGo se necessário

### Arquitetura Colaborativa

A proposta pede explicitamente:
> "decide which specialized agent **(or sequence of agents)** is best suited"

Por isso implementamos:
- **Single-Agent Flow:** Perguntas simples → 1 agente
- **Multi-Agent Flow:** Perguntas complexas → Support + Knowledge com context sharing

### Output Processing Layer

Separamos responsabilidades:
- **Core Agents:** Focam em dados (RAG, DB)
- **Output Processor:** Foca em qualidade (idioma, tom)

Benefícios:
- Consistência de linguagem
- Manutenibilidade
- Menos tokens gastos em cada agente

---

## 🤖 Uso de LLMs no Desenvolvimento

Este projeto foi desenvolvido com assistência de LLMs (Claude/GPT) para:

### Arquitetura & Design
- Discussão de trade-offs entre frameworks (CrewAI vs LangGraph)
- Design do fluxo multi-agent colaborativo
- Estrutura do RAG pipeline

### Implementação
- Scaffolding inicial do projeto
- Debugging de erros de integração CrewAI
- Otimização de prompts dos agentes

### Testes & Qualidade
- Geração de cenários de teste
- Identificação de edge cases
- Validação de consistência de linguagem

### Documentação
- Estruturação do README
- Diagramas de arquitetura (ASCII)
- PRD detalhado

**Nota:** Todo código foi revisado, testado e validado manualmente. LLMs foram usados como aceleradores, não substitutos do desenvolvimento.

---

## 📂 Estrutura do Projeto

```
cloudwalk-agent-swarm/
├── src/
│   ├── agents/           # Definição dos agentes
│   │   ├── router_agent.py
│   │   ├── knowledge_agent.py
│   │   ├── support_agent.py
│   │   └── output_processor.py
│   ├── rag/              # Pipeline RAG
│   │   ├── ingest.py
│   │   ├── search.py
│   │   └── urls.py
│   ├── tools/            # Ferramentas dos agentes
│   │   ├── rag_tool.py
│   │   ├── tavily_tool.py
│   │   └── support_tools.py
│   ├── db/               # Database SQLite
│   ├── main.py           # FastAPI app
│   ├── config.py         # Configurações
│   └── schemas.py        # Pydantic models
├── frontend/             # Interface web
├── tests/                # Testes pytest
├── scripts/              # Scripts auxiliares
├── data/                 # Dados persistentes
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── PRD.md               # Product Requirements Document
└── README.md            # Este arquivo
```

---

## 📄 Licença

Desenvolvido para o Desafio AI da CloudWalk.

---

**Autor:** Caio Garcia  
**Data:** Janeiro 2026
