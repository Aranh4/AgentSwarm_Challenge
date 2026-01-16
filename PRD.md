# PRD - CloudWalk Agent Swarm Challenge
## Product Requirements Document - Versão Executável

**Projeto:** Sistema Multi-Agente com RAG para InfinitePay  
**Data Início:** 13 de Janeiro de 2026 (Segunda-feira)  
**Data Entrega:** 23 de Janeiro de 2026 (Sexta-feira)  
**Prazo Total:** 10 dias úteis  
**Regime de Trabalho:** Sprint intensivo (4-6h/dia útil, 8-10h fim de semana)

---

## 🔥 DECISÕES TÉCNICAS CRÍTICAS (Atualizado 14/01/2026)

### ✅ VERSÕES ATUALIZADAS
- **CrewAI**: 0.121.1+ (era 0.1.26)
- **LangChain**: 1.2.3+ (era 0.1.4)
- **ChromaDB**: 0.5.0+ (era 0.4.22)
- **OpenAI**: 1.50.0+ (era 1.10.0)
- **Ver arquivo `MUDANCAS_PRD.md` para lista completa**

### ✅ ARQUITETURA MULTI-AGENT
- **APENAS execução SEQUENTIAL** (sem parallel)
- Context sharing via `context=[task1]` + `memory=True`
- Router força JSON com `response_format: json_object`

### ✅ INICIALIZAÇÃO AUTOMÁTICA
- Banco SQLite populado automaticamente no startup
- client789 garantido no seed (obrigatório para testes)
- RAG ingerido automaticamente se ChromaDB vazio

## 🚀 STATUS DO PROJETO (Atualizado 15/01/2026)

### ✅ CONCLUÍDO
- **Investigação & Arquitetura**: Definição da stack (CrewAI, LangChain, FastAPI).
- **Backend Base**: FastAPI setup, CORS, Logging, Pydantic Schemas.
- **RAG Pipeline**: Ingestão de 13 URLs InfinitePay, Chunking, Embeddings, ChromaDB.
- **Agentes Implementados**:
  - `Router`: Classificação Single/Multi-agent.
  - `Knowledge`: RAG + Web Search (Tavily).
  - `Support`: SQLite Mock + Tools de dados do usuário.
- **Tools**: `TavilyTool` (Fixed), `RagTool` (Fixed), Support Tools.
- **Frontend**: Chat UI funcional, "Debug Mode", Visualização de Sources.
- **Resiliência**: Correção de erros de validação LLM, Retry logic.
- **Consciência Temporal**: Agentes sabem a data atual (Jan 2026).

### ⏳ PRÓXIMOS PASSOS / REFINAMENTO
- [ ] Teste E2E completo final (Human Loop).
- [ ] Documentação de API (Swagger já existe, mas revisar).
- [ ] Cleanup de código (remover logs excessivos se houver).

### 📖 CHANGELOG
**Ver `MUDANCAS_PRD.md` para resumo completo das mudanças**

---

## 🎨 NOVA ARQUITETURA: Output Processing Agent (Jan 2026)

### Motivação
Durante os testes de validação, identificamos que misturar responsabilidades de **recuperação de dados** com **formatação de saída** no mesmo agente criava conflitos:
- RAG em Português influenciava a língua da resposta mesmo quando a query era em Inglês
- Agents gastavam tokens tentando "polir" texto em vez de focar em dados
- Difícil manter consistência de tom/linguagem entre múltiplos agents

### Solução: Separação de Responsabilidades

#### Camada 1: Core Agents (Foco em Dados)
**Knowledge Agent** e **Support Agent** agora têm **UMA responsabilidade**:
- Executar ferramentas (RAG, Web Search, DB Queries)
- Retornar dados brutos/factuais
- **NÃO** se preocupar com idioma final ou formatação para o usuário

#### Camada 2: Output Processing Agent (Foco em Qualidade)
Novo agente **pós-processador** que recebe a saída dos Core Agents e:
1. **Language Matching:** Garante que a resposta esteja no mesmo idioma da query do usuário
2. **Tone Adjustment:** Adapta o tom para o público InfinitePay (profissional, claro, amigável)
3. **Text Quality:** Melhora clareza, remove redundâncias, corrige gramática
4. **Brand Compliance:** Mantém termos técnicos consistentes (ex: "Maquininha Smart", não "máquina de cartão")

### Fluxo Atualizado

```
User Query → Router Agent
               ↓
        [Knowledge Agent] → Raw Response (pode estar em PT mesmo se query for EN)
               OR
        [Support Agent]   → Raw Response (dados do DB sem polish)
               ↓
    Output Processing Agent → Final Response:
               ↓                 - Idioma correto
               ↓                 - Tom InfinitePay
               ↓                 - Texto polido
        User Interface
```

### Benefícios
- **Simplicidade:** Core agents são mais simples (menos instruções no prompt)
- **Consistência:** Um único ponto para garantir qualidade de saída
- **Manutenibilidade:** Mudanças de tom/estilo em um lugar só
- **Separação de Custos:** Podemos usar modelos menores para core agents, modelo maior para output processing

### Implementação Técnica
- **Tipo:** Agent CrewAI com prompt especializado em reescrita
- **Ferramentas:** Nenhuma (apenas processa texto)
- **Temperatura:** 0.3 (permite criatividade para melhorar texto, mas mantém fatos)
- **Posição:** Executado após resposta final dos core agents, antes de retornar ao usuário

---

## 🎨 FRONTEND: Design System InfinitePay

### Paleta de Cores (Extraída da Página Oficial)

**Cores Primárias:**
- `--primary-green`: #CDFF00 (Lime/Neon Green - Accent principal)
- `--dark-bg`: #0A0A0A (Background escuro)
- `--dark-card`: #1A1A1A (Cards/Containers)

**Cores Secundárias:**
- `--text-primary`: #FFFFFF (Texto principal)
- `--text-secondary`: #A0A0A0 (Texto secundário/hints)
- `--border`: #2A2A2A (Divisores subtis)

**Cores de Status:**
- `--success`: #00FF88 (Confirmações)
- `--warning`: #FFD700 (Alertas)
- `--error`: #FF4444 (Erros)

### Tipografia
- **Font Family:** 'Inter', 'SF Pro Display', sans-serif (moderna, clean)
- **Headings:** 600-700 weight, tight letter-spacing
- **Body:** 400-500 weight, 1.6 line-height para legibilidade
- **Code/Data:** 'Fira Code', monospace

### Componentes UI

**Chat Bubble:**
- Background: `--dark-card`
- Border: 1px solid `--border`
- Border-radius: 12px
- Padding: 16px 20px
- Accent verde no lado esquerdo para mensagens do bot (3px solid `--primary-green`)

**Input Field:**
- Background: `--dark-card`
- Border: 1px solid `--border` (hover: `--primary-green`)
- Placeholder: `--text-secondary`
- Focus: box-shadow 0 0 0 2px rgba(205,255,0,0.2)

**Buttons:**
- Primary: Background `--primary-green`, Text `--dark-bg`, Bold
- Secondary: Border 1px `--primary-green`, Text `--primary-green`
- Hover: Slight glow effect (box-shadow)

**Agent Badge:**
- Small chip com ícone
- Knowledge: 📚 + lime green background (opacity 0.1)
- Support: 🎧 + blue accent
- Router: 🔀 + purple accent

### Layout
- **Sidebar:** Minimal, dark background, lime green highlights
- **Chat Area:** Centralizado, max-width 900px, fundo escuro limpo
- **Header:** Sticky, logo InfinitePay (se disponível), botão "Debug Mode"

### Animações
- **Typing Indicator:** 3 dots pulsando em verde
- **Message Appear:** Fade-in + slide-up (200ms)
- **Hover Effects:** Smooth transitions (150ms ease)

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Requisitos do Desafio](#requisitos-do-desafio)
3. [Stack Técnica](#stack-técnica)
4. [Arquitetura do Sistema](#arquitetura-do-sistema)
5. [Estrutura de Pastas](#estrutura-de-pastas)
6. [Especificação Detalhada dos Componentes](#especificação-detalhada-dos-componentes)
7. [Implementação Passo-a-Passo](#implementação-passo-a-passo)
8. [Cronograma de 10 Dias](#cronograma-de-10-dias)
9. [Cenários de Teste](#cenários-de-teste)
10. [Checklist de Qualidade](#checklist-de-qualidade)
11. [Guia de Desenvolvimento com Cursor](#guia-de-desenvolvimento-com-cursor)

---

## 🎯 Visão Geral

### O que é o projeto?

Sistema multi-agente (agent swarm) que processa mensagens de usuários através de **3 agentes especializados** colaborando entre si:

1. **Router Agent** - Analisa e roteia mensagens
2. **Knowledge Agent** - Responde usando RAG (InfinitePay) ou web search (perguntas gerais)
3. **Customer Support Agent** - Resolve problemas consultando dados do cliente

### Por que essa arquitetura?

- **Separação de responsabilidades:** Cada agente tem expertise específica
- **Escalabilidade:** Fácil adicionar novos agentes
- **Manutenibilidade:** Lógica isolada por domínio
- **Demonstração de conhecimento:** Mostra domínio de agent orchestration moderna
- **⭐ Colaboração Multi-Agent:** Agentes podem trabalhar **juntos** compartilhando contexto (requisito explícito da proposta!)

### 🔥 DIFERENCIAL: Arquitetura Colaborativa

**A proposta pede explicitamente** (linha 19-20):
> "decide which specialized agent **(or sequence of agents)** is best suited to handle it.  
> It will manage the **workflow and data flow between other agents**."

Isso significa que **NÃO É** apenas roteamento simples! O sistema deve suportar:

1. **Single-Agent Flow:** Perguntas simples → 1 agente resolve
2. **Sequential Multi-Agent Flow:** Perguntas complexas → Agente A gera contexto → Agente B usa esse contexto → Resposta integrada
3. **Context Sharing:** Dados do Support Agent informam o Knowledge Agent

**Exemplo prático:**
- ❌ **Ruim:** "Qual maquininha é melhor?" → Knowledge responde genericamente
- ✅ **BOM:** "Qual maquininha é melhor?" → Support busca perfil do cliente → Knowledge usa esse contexto → Resposta **personalizada**

### Resultado esperado

API REST que recebe mensagens de usuários e retorna respostas contextualizadas, escolhendo automaticamente o melhor agente para cada tipo de pergunta.

---

## 📝 Requisitos do Desafio

### Core Requirements (OBRIGATÓRIOS)

#### 1. Agent Swarm com 3 Agentes

**Router Agent:**
- Entry point para todas as mensagens
- Analisa intent e roteia para agente especializado
- Gerencia workflow e data flow

**Knowledge Agent:**
- Responde perguntas sobre InfinitePay usando RAG
- Busca informações gerais usando web search
- Fundamenta respostas em fontes confiáveis

**Customer Support Agent:**
- Acessa dados de clientes
- Resolve problemas técnicos/operacionais
- Mínimo 2 tools funcionais

#### 2. API REST

**Endpoint obrigatório:**
```
POST /chat
Body: {
  "message": "string",
  "user_id": "string"
}
Response: {
  "response": "string",
  "agent_used": "string",
  "sources": ["string"]
}
```

#### 3. RAG Pipeline

**Fontes de dados (13 URLs InfinitePay):**
- https://www.infinitepay.io
- https://www.infinitepay.io/maquininha
- https://www.infinitepay.io/maquininha-celular
- https://www.infinitepay.io/tap-to-pay
- https://www.infinitepay.io/pdv
- https://www.infinitepay.io/receba-na-hora
- https://www.infinitepay.io/gestao-de-cobranca-2
- https://www.infinitepay.io/link-de-pagamento
- https://www.infinitepay.io/loja-online
- https://www.infinitepay.io/boleto
- https://www.infinitepay.io/conta-digital
- https://www.infinitepay.io/pix
- https://www.infinitepay.io/emprestimo
- https://www.infinitepay.io/cartao
- https://www.infinitepay.io/rendimento
- https://www.infinitepay.io/taxas

**Pipeline deve:**
- Fazer scraping das URLs
- Processar e chunkar conteúdo
- Gerar embeddings
- Armazenar em vector store
- Permitir retrieval por similaridade

#### 4. Dockerização

- Dockerfile funcional
- docker-compose.yml (se necessário)
- Fácil de rodar: `docker-compose up`
- Dados persistem entre restarts

#### 5. Testes

- Estratégia de testes documentada
- Alguns testes básicos implementados
- Explicar como expandir para integration tests

#### 6. Documentação

**README.md deve conter:**
- Instruções de setup
- Explicação da arquitetura
- Design decisions
- Como funciona o RAG
- Como rodar testes
- **Como você usou LLMs para desenvolver**

### Bonus Features (OPCIONAIS - se sobrar tempo)

- Guardrails para filtrar perguntas/respostas indesejadas
- 4º agente custom
- Mecanismo de redirect to human

---

## 🛠️ Stack Técnica

### Decisões Técnicas Finais

| Categoria | Tecnologia | Justificativa |
|-----------|-----------|---------------|
| **Linguagem** | Python 3.11+ | Ecosystem rico para AI/ML, requisito comum |
| **API Framework** | FastAPI | Moderno, rápido, type hints nativos, async |
| **Agent Framework** | CrewAI | Especializado em agent swarms, código limpo |
| **LLM** | OpenAI GPT-3.5-turbo | Custo-benefício, rápido, suficiente |
| **Embeddings** | text-embedding-3-small | Otimizado para RAG, barato |
| **Vector Store** | ChromaDB | Local, fácil dockerizar, sem dependências externas |
| **Web Search** | DuckDuckGo | Gratuito, SEM API key adicional |
| **Mock DB** | SQLite | Leve, incluso no Python, perfeito para mock |
| **Container** | Docker + compose | Standard da indústria |
| **Testes** | pytest | Standard Python |

### Dependencies Completas

**⚠️ NOTA:** Versões atualizadas para Janeiro de 2026. Use `pip install --upgrade` para garantir compatibilidade.

```txt
# FastAPI & Server
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.3
pydantic-settings>=2.1.0
python-dotenv>=1.0.0

# LLM & AI (ATUALIZADAS 2026)
openai>=1.50.0
langchain>=1.2.3
langchain-core>=1.2.7
langchain-openai>=0.2.0
langchain-community>=0.3.0
crewai>=0.121.1
crewai-tools>=1.8.0

# RAG & Vector Store (ATUALIZADAS 2026)
chromadb>=0.5.0
beautifulsoup4>=4.12.3
lxml>=5.1.0

# Tools
duckduckgo-search>=6.0.0

# Testing
pytest>=8.0.0
pytest-asyncio>=0.23.3
httpx>=0.27.0
```

**Comandos de instalação:**
```bash
# Instalar todas as dependências
pip install --upgrade -r requirements.txt

# Ou instalar individualmente as principais
pip install --upgrade crewai crewai-tools langchain langchain-openai chromadb openai
```

---

## 🏗️ Arquitetura do Sistema

### Diagrama de Fluxo Completo (Arquitetura Colaborativa)

```
┌─────────────┐
│   User      │
│  Request    │
└──────┬──────┘
       │
       │ POST /chat {"message": "...", "user_id": "..."}
       ▼
┌──────────────────────────────────────────────────┐
│           FastAPI Application                    │
│  - Pydantic validation                          │
│  - Logging & Error handling                     │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────┐
│          CrewAI Crew Manager                     │
│  - Detecta single vs multi-agent                │
│  - Gerencia context sharing entre tasks          │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │   ROUTER AGENT      │
         │  Analisa & decide:  │
         │  - Categoria        │
         │  - Single/Multi     │
         │  - Agents needed    │
         └──────────┬──────────┘
                    │
       ┌────────────┴────────────┐
       │                         │
   SINGLE AGENT             MULTI-AGENT
       │                    (COLLABORATION!)
       │                         │
       │              ┌──────────┴──────────┐
       │              │                     │
       │         TASK 1 (Support)      TASK 2 (Knowledge)
       │              │                     │
       │              │ Busca contexto      │ Usa contexto
       │              │ do cliente          │ da Task 1
       │              │                     │
       │              ▼                     ▼
       │    ┌──────────────────┐  ┌──────────────────┐
       │    │ Customer Support │  │   Knowledge      │
       │    │     Agent        │  │     Agent        │
       │    │                  │  │                  │
       │    │ Tools:           │  │ Tools:           │
       │    │ - get_user_data  │  │ - RAG search     │
       │    │ - get_txns       │  │ - Web search     │
       │    └────────┬─────────┘  └─────────┬────────┘
       │             │                       │
       │             ▼                       ▼
       │    ┌──────────────┐       ┌──────────────┐
       │    │ SQLite Mock  │       │  ChromaDB    │
       │    │ - users      │       │  (13 URLs)   │
       │    │ - txns       │       │  DuckDuckGo  │
       │    └──────────────┘       └──────────────┘
       │             │                       │
       │             │   CONTEXT SHARING     │
       │             │   ════════════════>   │
       │             │                       │
       │             └───────────┬───────────┘
       │                         │
       └─────────────────────────┤
                                 │
                                 ▼
                        ┌────────────────┐
                        │   Response     │
                        │   Integrada    │
                        │  (Personalizada)│
                        └────────────────┘
```

**Legenda:**
- **Setas simples (→):** Fluxo normal
- **Setas duplas (═>):** Context sharing entre agentes!
- **TASK 1 → TASK 2:** Execução sequencial com context

### Fluxo de Dados Detalhado

#### ⚠️ IMPORTANTE: Arquitetura Colaborativa Multi-Agent

A proposta **explicitamente** pede que os agentes possam **colaborar** (linha 19: "sequence of agents", linha 20: "data flow between other agents"). Não é apenas roteamento simples!

**Tipos de fluxo:**
1. **Single Agent:** Pergunta simples → 1 agente responde
2. **Sequential Multi-Agent:** Pergunta complexa → Agente A passa contexto para Agente B → Resposta combinada

**⚠️ DECISÃO TÉCNICA:** Utilizaremos **apenas execução sequencial** (Process.sequential). Isso:
- Facilita o compartilhamento de contexto entre tasks
- Simplifica a implementação inicial
- Garante ordem de execução previsível
- Permite debugging mais fácil

---

#### Cenário 1: Single Agent - Pergunta sobre InfinitePay

```
User: "Quais as taxas da maquininha smart?"
  ↓
FastAPI recebe request
  ↓
Crew Manager inicia processamento
  ↓
Router Agent classifica → "infinitepay_product" (apenas Knowledge necessário)
  ↓
Knowledge Agent acionado (modo RAG)
  ↓
RAG Tool busca no ChromaDB:
  - Embedding da pergunta
  - Similarity search
  - Top 5 chunks relevantes
  ↓
LLM gera resposta usando chunks como contexto
  ↓
Response: {
  "response": "A Maquininha Smart da InfinitePay...",
  "agent_used": "Knowledge Agent",
  "sources": ["https://www.infinitepay.io/maquininha"]
}
```

#### Cenário 2: Single Agent - Pergunta geral

```
User: "Quando foi o último jogo do Palmeiras?"
  ↓
Router Agent classifica → "general_question"
  ↓
Knowledge Agent acionado (modo Web Search)
  ↓
DuckDuckGo Tool busca na web
  ↓
LLM sintetiza resultados
  ↓
Response com informações atualizadas
```

#### Cenário 3: Single Agent - Problema de suporte simples

```
User: "Por que não consigo fazer transferências?" (user_id: client789)
  ↓
Router Agent classifica → "customer_support"
  ↓
Customer Support Agent acionado
  ↓
Tools executadas:
  1. get_user_data(client789) → status conta, plano
  2. get_recent_transactions(client789) → últimas transações
  ↓
LLM analisa dados e diagnostica problema
  ↓
Response personalizada com dados do cliente
```

#### ⭐ Cenário 4: MULTI-AGENT - Recomendação Personalizada

```
User: "Qual maquininha da InfinitePay é melhor para meu negócio?"
  ↓
Router Agent classifica → "multi_agent_needed" 
  (precisa de dados do cliente + conhecimento de produtos)
  ↓
TASK 1: Customer Support Agent
  ↓
  Busca perfil do cliente:
  - Volume médio de transações
  - Tipo de negócio
  - Plano atual
  ↓
  Context: {
    "user_profile": "Restaurante, 200 transações/mês, plano básico",
    "avg_ticket": "R$ 45"
  }
  ↓
TASK 2: Knowledge Agent (recebe context de Task 1)
  ↓
  Busca informações sobre maquininhas no RAG com filtro:
  - Adequadas para restaurantes
  - Volume de 200 transações/mês
  ↓
  Analisa: Smart vs Tap-to-Pay vs PDV
  ↓
TASK 3: Synthesis (CrewAI combina outputs)
  ↓
Response: {
  "response": "Com base no seu perfil (restaurante, 200 trans/mês), 
              recomendo a Maquininha Smart porque...",
  "agent_used": "Customer Support + Knowledge Agent (collaborative)",
  "sources": ["user_data", "https://www.infinitepay.io/maquininha"]
}
```

#### ⭐ Cenário 5: MULTI-AGENT - Troubleshooting Avançado

```
User: "Minha última transação Pix foi recusada. O que houve?"
  ↓
Router classifica → "multi_agent_needed"
  ↓
TASK 1: Customer Support Agent
  ↓
  Busca detalhes da transação:
  - Tipo: Pix
  - Valor: R$ 1500
  - Status: failed
  - Erro: "limit_exceeded"
  ↓
  Context: {
    "transaction_details": {...},
    "user_plan": "basic",
    "daily_limit": "R$ 1000"
  }
  ↓
TASK 2: Knowledge Agent (recebe context)
  ↓
  Busca no RAG sobre:
  - Políticas de limite Pix
  - Como aumentar limites
  - Diferenças entre planos
  ↓
TASK 3: Synthesis
  ↓
Response: {
  "response": "Sua transação de R$ 1500 foi recusada porque excedeu 
              o limite diário de R$ 1000 do plano básico. 
              Para aumentar: [instruções do RAG]",
  "agent_used": "Customer Support + Knowledge Agent",
  "sources": ["transaction_logs", "https://www.infinitepay.io/pix"]
}
```

#### ⭐ Cenário 6: MULTI-AGENT - Contexto + Informação (Sequential)

```
User: "Como funciona o Pix parcelado e eu posso usar?"
  ↓
Router classifica → "multi_agent_needed"
  ↓
SEQUENTIAL EXECUTION:
  ↓
TASK 1: Customer Support Agent
  Verifica elegibilidade do cliente (plano, status)
  Output: {"plan": "premium", "eligible": true}
  ↓
TASK 2: Knowledge Agent (recebe context de Task 1)
  Busca explicação de Pix parcelado no RAG
  Personaliza resposta com base na elegibilidade
  ↓
Response final combina:
  - Explicação técnica (Knowledge)
  - Status de elegibilidade personalizado (usando context)
```

**⚠️ NOTA:** Removemos execução paralela. Todas as colaborações multi-agent usam Process.sequential.

---

## 📁 Estrutura de Pastas

```
cloudwalk-agent-swarm/
│
├── src/                          # Código fonte principal
│   ├── __init__.py
│   ├── main.py                   # FastAPI app + startup logic
│   ├── config.py                 # Configurações do .env
│   ├── schemas.py                # Pydantic models (Request/Response)
│   │
│   ├── agents/                   # Definição dos agentes
│   │   ├── __init__.py
│   │   ├── router.py             # Router Agent
│   │   ├── knowledge.py          # Knowledge Agent
│   │   └── support.py            # Customer Support Agent
│   │
│   ├── crew/                     # Orquestração CrewAI
│   │   ├── __init__.py
│   │   └── manager.py            # Crew setup e task execution
│   │
│   ├── rag/                      # RAG Pipeline
│   │   ├── __init__.py
│   │   ├── ingest.py             # Scraping + embedding + storage
│   │   ├── search.py             # Retrieval logic
│   │   └── urls.py               # Lista das 13 URLs
│   │
│   └── tools/                    # Tools para os agentes
│       ├── __init__.py
│       ├── rag_tool.py           # RAG search como CrewAI Tool
│       ├── web_tool.py           # DuckDuckGo wrapper
│       └── support_tools.py      # User data + transactions tools
│
├── scripts/                      # Scripts auxiliares
│   ├── seed_db.py                # Popular SQLite com dados mock
│   └── test_ingest.py            # Testar ingestão RAG isoladamente
│
├── tests/                        # Testes
│   ├── __init__.py
│   ├── test_api.py               # Testes dos endpoints
│   ├── test_rag.py               # Testes do RAG pipeline
│   ├── test_crew.py              # Testes da orquestração
│   └── conftest.py               # Fixtures pytest
│
├── data/                         # Dados persistentes (GITIGNORED)
│   ├── chromadb/                 # Vector store
│   └── customers.db              # SQLite database
│
├── docs/                         # Documentação adicional
│   └── TESTING_STRATEGY.md       # Estratégia de testes detalhada
│
├── .env                          # Variáveis de ambiente (GITIGNORED)
├── .env.example                  # Template do .env
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── pytest.ini                    # Configuração pytest
├── Dockerfile                    # Container definition
├── docker-compose.yml            # Multi-container orchestration
├── README.md                     # Documentação principal
└── PRD.md                        # Este documento
```

---

## 🔧 Especificação Detalhada dos Componentes

### 1. FastAPI Application (src/main.py)

**Responsabilidades:**
- Expor endpoints HTTP
- Validar requests
- Gerenciar lifecycle (startup/shutdown)
- Logging estruturado
- Error handling global

**Implementação:**

```python
"""
src/main.py - FastAPI Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from src.schemas import ChatRequest, ChatResponse
from src.crew.manager import AgentSwarmManager
from src.rag.ingest import ingest_if_empty
from src.config import settings

# Setup logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup e shutdown events"""
    logger.info("Iniciando aplicação...")
    
    # Startup 1: Popular banco SQLite se vazio
    try:
        from scripts.seed_db import seed_if_empty
        seed_if_empty()
        logger.info("Banco de dados SQLite verificado/populado")
    except Exception as e:
        logger.error(f"Erro ao popular banco: {e}")
        raise
    
    # Startup 2: Ingerir dados RAG se ChromaDB vazio
    try:
        ingest_if_empty()
        logger.info("RAG pipeline pronto")
    except Exception as e:
        logger.error(f"Erro na ingestão: {e}")
        raise
    
    # Startup 3: Inicializar Crew Manager
    app.state.crew_manager = AgentSwarmManager()
    logger.info("Agent Swarm inicializado")
    
    yield
    
    # Shutdown
    logger.info("Encerrando aplicação...")

# Create app
app = FastAPI(
    title="CloudWalk Agent Swarm",
    description="Sistema multi-agente com RAG para InfinitePay",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {
        "status": "healthy",
        "environment": settings.environment
    }

# Main endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Processa mensagem através do agent swarm
    
    Args:
        request: ChatRequest com message e user_id
        
    Returns:
        ChatResponse com resposta, agente usado e fontes
    """
    try:
        logger.info(f"Processando mensagem de {request.user_id}: {request.message[:50]}...")
        
        # Processar através do Crew
        result = app.state.crew_manager.process_message(
            message=request.message,
            user_id=request.user_id
        )
        
        logger.info(f"Resposta gerada por {result['agent_used']}")
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar mensagem: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development"
    )
```

**Pontos-chave:**
- ✅ Usa `lifespan` para gerenciar startup (ingestão RAG)
- ✅ State management via `app.state` para o Crew Manager
- ✅ Logging detalhado para debugging
- ✅ Error handling com HTTPException
- ✅ Type hints + Pydantic validation

---

### 2. Schemas (src/schemas.py)

**Responsabilidades:**
- Definir contratos de API
- Validação automática de dados
- Documentação OpenAPI

**Implementação:**

```python
"""
src/schemas.py - Pydantic Models
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class ChatRequest(BaseModel):
    """Request para o endpoint /chat"""
    message: str = Field(..., description="Mensagem do usuário", min_length=1)
    user_id: str = Field(..., description="Identificador do usuário")
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "message": "Quais as taxas da maquininha smart?",
                "user_id": "client789"
            }]
        }
    }


class ChatResponse(BaseModel):
    """Response do endpoint /chat"""
    response: str = Field(..., description="Resposta gerada pelo agente")
    agent_used: str = Field(..., description="Nome do agente que processou")
    sources: List[str] = Field(
        default_factory=list,
        description="Fontes consultadas (URLs ou referências)"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "response": "A Maquininha Smart tem taxa de 1,99% no débito...",
                "agent_used": "Knowledge Agent",
                "sources": ["https://www.infinitepay.io/maquininha"]
            }]
        }
    }
```

---

### 3. Configurações (src/config.py)

**Responsabilidades:**
- Carregar variáveis de ambiente
- Validar configurações obrigatórias
- Fornecer defaults sensatos

**Implementação:**

```python
"""
src/config.py - Configurações da aplicação
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configurações carregadas do .env"""
    
    # OpenAI (OBRIGATÓRIA)
    openai_api_key: str = Field(..., description="API key da OpenAI")
    
    # Application
    environment: str = Field(default="development", description="Ambiente de execução")
    log_level: str = Field(default="INFO", description="Nível de logging")
    api_host: str = Field(default="0.0.0.0", description="Host da API")
    api_port: int = Field(default=8000, description="Porta da API")
    
    # Paths
    chroma_persist_dir: str = Field(
        default="./data/chromadb",
        description="Diretório de persistência do ChromaDB"
    )
    sqlite_db_path: str = Field(
        default="./data/customers.db",
        description="Caminho do banco SQLite"
    )
    
    # LLM Config
    default_model: str = Field(default="gpt-3.5-turbo", description="Modelo LLM padrão")
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="Modelo de embeddings"
    )
    max_tokens: int = Field(default=1000, description="Máximo de tokens por resposta")
    temperature: float = Field(default=0.7, description="Temperature do LLM")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instância global
settings = Settings()
```

---

### 4. RAG Pipeline

#### 4.1 URLs (src/rag/urls.py)

```python
"""
src/rag/urls.py - URLs para ingestão
"""

INFINITEPAY_URLS = [
    "https://www.infinitepay.io",
    "https://www.infinitepay.io/maquininha",
    "https://www.infinitepay.io/maquininha-celular",
    "https://www.infinitepay.io/tap-to-pay",
    "https://www.infinitepay.io/pdv",
    "https://www.infinitepay.io/receba-na-hora",
    "https://www.infinitepay.io/gestao-de-cobranca-2",
    "https://www.infinitepay.io/link-de-pagamento",
    "https://www.infinitepay.io/loja-online",
    "https://www.infinitepay.io/boleto",
    "https://www.infinitepay.io/conta-digital",
    "https://www.infinitepay.io/pix",
    "https://www.infinitepay.io/emprestimo",
    "https://www.infinitepay.io/cartao",
    "https://www.infinitepay.io/rendimento"
]
```

#### 4.2 Ingestão (src/rag/ingest.py)

**Responsabilidades:**
- Scraping das 13 URLs
- Chunking de documentos
- Geração de embeddings
- Armazenamento no ChromaDB
- Persistência em disco

**Implementação:**

```python
"""
src/rag/ingest.py - Pipeline de ingestão RAG
"""
import chromadb
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import logging
from pathlib import Path

from src.rag.urls import INFINITEPAY_URLS
from src.config import settings

logger = logging.getLogger(__name__)

def create_chroma_client():
    """Cria cliente ChromaDB com persistência"""
    persist_dir = Path(settings.chroma_persist_dir)
    persist_dir.mkdir(parents=True, exist_ok=True)
    
    client = chromadb.PersistentClient(path=str(persist_dir))
    return client

def ingest_documents():
    """
    Ingere documentos das URLs do InfinitePay
    
    Pipeline:
    1. Load - WebBaseLoader
    2. Split - RecursiveCharacterTextSplitter
    3. Embed - OpenAI embeddings
    4. Store - ChromaDB
    
    Returns:
        int: Número de chunks ingeridos
    """
    logger.info(f"Iniciando ingestão de {len(INFINITEPAY_URLS)} URLs...")
    
    # 1. Load documents
    loader = WebBaseLoader(INFINITEPAY_URLS)
    logger.info("Fazendo scraping das páginas...")
    documents = loader.load()
    logger.info(f"Carregados {len(documents)} documentos")
    
    # 2. Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Criados {len(chunks)} chunks")
    
    # 3. Setup ChromaDB
    client = create_chroma_client()
    
    # Deletar collection se já existe (fresh start)
    try:
        client.delete_collection("infinitepay_docs")
    except:
        pass
    
    collection = client.create_collection(
        name="infinitepay_docs",
        metadata={"description": "Documentação InfinitePay para RAG"}
    )
    
    # 4. Embed and store
    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key
    )
    
    logger.info("Gerando embeddings e armazenando...")
    
    # Processar em batches
    batch_size = 50
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        
        # Extrair textos e metadados
        texts = [chunk.page_content for chunk in batch]
        metadatas = [chunk.metadata for chunk in batch]
        ids = [f"doc_{i+j}" for j in range(len(batch))]
        
        # Gerar embeddings
        batch_embeddings = embeddings.embed_documents(texts)
        
        # Adicionar à collection
        collection.add(
            ids=ids,
            embeddings=batch_embeddings,
            documents=texts,
            metadatas=metadatas
        )
        
        logger.info(f"Processados {i + len(batch)}/{len(chunks)} chunks")
    
    logger.info(f"✅ Ingestão completa: {len(chunks)} chunks armazenados")
    return len(chunks)

def ingest_if_empty():
    """
    Verifica se ChromaDB está vazio e ingere se necessário
    
    Chamado no startup da aplicação
    """
    client = create_chroma_client()
    
    try:
        collection = client.get_collection("infinitepay_docs")
        count = collection.count()
        
        if count > 0:
            logger.info(f"ChromaDB já populado com {count} documentos")
            return
    except:
        pass
    
    logger.info("ChromaDB vazio, iniciando ingestão...")
    ingest_documents()
```

**Pontos-chave:**
- ✅ Chunking com overlap para não perder contexto
- ✅ Batch processing para eficiência
- ✅ Metadata preservada (source URL)
- ✅ Persistência automática no disco
- ✅ Verificação para não reingerir

#### 4.3 Search/Retrieval (src/rag/search.py)

**Responsabilidades:**
- Buscar documentos relevantes por similaridade
- Retornar chunks + metadata
- Formatação para consumo pelo LLM

**Implementação:**

```python
"""
src/rag/search.py - Retrieval de documentos
"""
import chromadb
from langchain_openai import OpenAIEmbeddings
from typing import List, Dict
import logging

from src.config import settings

logger = logging.getLogger(__name__)

class RAGSearcher:
    """Classe para buscar documentos no ChromaDB"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self.collection = self.client.get_collection("infinitepay_docs")
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Busca documentos similares à query
        
        Args:
            query: Pergunta do usuário
            top_k: Número de documentos a retornar
            
        Returns:
            Lista de dicts com 'content', 'source' e 'score'
        """
        logger.info(f"Buscando documentos para: {query[:50]}...")
        
        # Gerar embedding da query
        query_embedding = self.embeddings.embed_query(query)
        
        # Buscar no ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Formatar resultados
        documents = []
        for i in range(len(results['ids'][0])):
            doc = {
                'content': results['documents'][0][i],
                'source': results['metadatas'][0][i].get('source', 'unknown'),
                'score': results['distances'][0][i] if 'distances' in results else 0
            }
            documents.append(doc)
        
        logger.info(f"Encontrados {len(documents)} documentos relevantes")
        return documents
    
    def format_context(self, documents: List[Dict]) -> str:
        """
        Formata documentos como contexto para o LLM
        
        Args:
            documents: Lista de documentos retornados pela busca
            
        Returns:
            String formatada para usar como contexto
        """
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"[Fonte {i}: {doc['source']}]\n{doc['content']}\n")
        
        return "\n---\n".join(context_parts)
```

---

### 5. Tools para Agentes

#### 5.1 RAG Tool (src/tools/rag_tool.py)

**Responsabilidades:**
- Wrapper do RAG searcher como CrewAI Tool
- Interface clara para o agente

**Implementação:**

```python
"""
src/tools/rag_tool.py - RAG como CrewAI Tool
"""
from crewai_tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

from src.rag.search import RAGSearcher

class RAGSearchInput(BaseModel):
    """Input para RAG search tool"""
    query: str = Field(..., description="Pergunta sobre produtos/serviços InfinitePay")

class RAGSearchTool(BaseTool):
    name: str = "Buscar Conhecimento InfinitePay"
    description: str = (
        "Busca informações sobre produtos e serviços da InfinitePay. "
        "Use para responder perguntas sobre maquininhas, taxas, conta digital, "
        "Pix, cartões, empréstimos, etc. "
        "Retorna informações extraídas do site oficial."
    )
    args_schema: Type[BaseModel] = RAGSearchInput
    
    def __init__(self):
        super().__init__()
        self.searcher = RAGSearcher()
    
    def _run(self, query: str) -> str:
        """
        Executa busca no RAG
        
        Args:
            query: Pergunta do usuário
            
        Returns:
            Contexto formatado com informações relevantes
        """
        documents = self.searcher.search(query, top_k=5)
        context = self.searcher.format_context(documents)
        
        return f"""Informações encontradas sobre: {query}

{context}

Use essas informações para responder à pergunta do usuário de forma clara e precisa.
Sempre cite a fonte das informações."""
```

#### 5.2 Web Search Tool (src/tools/web_tool.py)

**Implementação:**

```python
"""
src/tools/web_tool.py - DuckDuckGo Search Tool
"""
from crewai_tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from duckduckgo_search import DDGS
import logging

logger = logging.getLogger(__name__)

class WebSearchInput(BaseModel):
    """Input para web search"""
    query: str = Field(..., description="Termo de busca na web")

class WebSearchTool(BaseTool):
    name: str = "Buscar na Web"
    description: str = (
        "Busca informações atualizadas na internet usando DuckDuckGo. "
        "Use para perguntas gerais sobre notícias, esportes, eventos atuais, "
        "ou qualquer informação que não esteja relacionada aos produtos InfinitePay. "
        "Retorna resumo dos resultados encontrados."
    )
    args_schema: Type[BaseModel] = WebSearchInput
    
    def _run(self, query: str) -> str:
        """
        Busca na web via DuckDuckGo
        
        Args:
            query: Termo de busca
            
        Returns:
            Resultados formatados
        """
        try:
            logger.info(f"Buscando na web: {query}")
            
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
            
            if not results:
                return "Nenhum resultado encontrado."
            
            # Formatar resultados
            formatted = [f"Resultados da busca por '{query}':\n"]
            
            for i, result in enumerate(results, 1):
                formatted.append(
                    f"{i}. {result['title']}\n"
                    f"   {result['body']}\n"
                    f"   Fonte: {result['href']}\n"
                )
            
            return "\n".join(formatted)
            
        except Exception as e:
            logger.error(f"Erro na busca web: {e}")
            return f"Erro ao buscar na web: {str(e)}"
```

#### 5.3 Customer Support Tools (src/tools/support_tools.py)

**Implementação:**

```python
"""
src/tools/support_tools.py - Tools de suporte ao cliente
"""
import sqlite3
from crewai_tools import BaseTool
from typing import Type, Dict, List
from pydantic import BaseModel, Field
import logging
import json

from src.config import settings

logger = logging.getLogger(__name__)

# ========== GET USER DATA TOOL ==========

class GetUserDataInput(BaseModel):
    """Input para get user data"""
    user_id: str = Field(..., description="ID do usuário")

class GetUserDataTool(BaseTool):
    name: str = "Obter Dados do Usuário"
    description: str = (
        "Obtém informações do cliente como nome, email, status da conta e plano. "
        "Use quando precisar de contexto sobre o usuário para resolver problemas."
    )
    args_schema: Type[BaseModel] = GetUserDataInput
    
    def _run(self, user_id: str) -> str:
        """
        Busca dados do usuário no SQLite
        
        Args:
            user_id: ID do usuário
            
        Returns:
            JSON string com dados do usuário
        """
        try:
            conn = sqlite3.connect(settings.sqlite_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, name, email, account_status, plan, created_at
                FROM users
                WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return f"Usuário {user_id} não encontrado no sistema."
            
            user_data = dict(row)
            return json.dumps(user_data, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados do usuário: {e}")
            return f"Erro ao acessar dados do usuário: {str(e)}"

# ========== GET TRANSACTIONS TOOL ==========

class GetTransactionsInput(BaseModel):
    """Input para get transactions"""
    user_id: str = Field(..., description="ID do usuário")
    limit: int = Field(default=10, description="Número de transações a retornar")

class GetRecentTransactionsTool(BaseTool):
    name: str = "Obter Transações Recentes"
    description: str = (
        "Obtém as transações mais recentes do cliente. "
        "Use para investigar problemas com pagamentos, transferências ou histórico financeiro."
    )
    args_schema: Type[BaseModel] = GetTransactionsInput
    
    def _run(self, user_id: str, limit: int = 10) -> str:
        """
        Busca transações do usuário
        
        Args:
            user_id: ID do usuário
            limit: Número máximo de transações
            
        Returns:
            JSON string com transações
        """
        try:
            conn = sqlite3.connect(settings.sqlite_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT transaction_id, amount, type, status, created_at
                FROM transactions
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return f"Nenhuma transação encontrada para o usuário {user_id}."
            
            transactions = [dict(row) for row in rows]
            return json.dumps(transactions, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Erro ao buscar transações: {e}")
            return f"Erro ao acessar transações: {str(e)}"
```

---

### 6. Agentes CrewAI

#### 6.1 Router Agent (src/agents/router.py)

**Responsabilidade:** Classificar intenção da mensagem

**Implementação:**

```python
"""
src/agents/router.py - Router Agent
"""
from crewai import Agent
from langchain_openai import ChatOpenAI

from src.config import settings

def create_router_agent() -> Agent:
    """
    Cria o Router Agent com JSON parsing via Pydantic
    
    Responsável por classificar mensagens e determinar qual agente deve processar.
    Usa structured output para garantir JSON válido.
    """
    llm = ChatOpenAI(
        model=settings.default_model,
        temperature=0.3,  # Mais determinístico para classificação
        openai_api_key=settings.openai_api_key,
        model_kwargs={
            "response_format": {"type": "json_object"}  # Force JSON output
        }
    )
    
    agent = Agent(
        role="Roteador de Mensagens",
        goal="Analisar mensagens de usuários e classificar corretamente a intenção para direcionar ao agente especializado apropriado. SEMPRE retornar JSON válido.",
        backstory="""Você é um especialista em classificação de intenções com profundo 
        conhecimento sobre produtos financeiros da InfinitePay e atendimento ao cliente.
        
        Você analisa cada mensagem e determina:
        - Se é sobre PRODUTOS/SERVIÇOS da InfinitePay (maquininhas, taxas, Pix, conta digital, etc)
        - Se é PROBLEMA DE SUPORTE (login, transferências, bugs, questões técnicas)
        - Se é PERGUNTA GERAL (notícias, esportes, informações não relacionadas à InfinitePay)
        - Se precisa de MÚLTIPLOS AGENTES (recomendação personalizada, troubleshooting avançado)
        
        Sua classificação é precisa e consistente.
        
        **IMPORTANTE:** Você SEMPRE retorna JSON válido no formato:
        {
          "category": "CATEGORIA",
          "strategy": "single" ou "multi_agent",
          "agents_needed": ["agent1", "agent2"],
          "reasoning": "breve justificativa"
        }""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    return agent
```

#### 6.2 Knowledge Agent (src/agents/knowledge.py)

**Responsabilidade:** Responder usando RAG ou Web Search

**Implementação:**

```python
"""
src/agents/knowledge.py - Knowledge Agent
"""
from crewai import Agent
from langchain_openai import ChatOpenAI
from typing import List

from src.config import settings
from src.tools.rag_tool import RAGSearchTool
from src.tools.web_tool import WebSearchTool

def create_knowledge_agent() -> Agent:
    """
    Cria o Knowledge Agent
    
    Responsável por responder perguntas usando:
    - RAG para informações sobre InfinitePay
    - Web search para perguntas gerais
    """
    llm = ChatOpenAI(
        model=settings.default_model,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
        openai_api_key=settings.openai_api_key
    )
    
    # Instanciar tools
    rag_tool = RAGSearchTool()
    web_tool = WebSearchTool()
    
    agent = Agent(
        role="Especialista em Conhecimento",
        goal="""Fornecer informações precisas e úteis respondendo perguntas sobre 
        produtos/serviços InfinitePay (usando RAG) ou perguntas gerais (usando busca na web)""",
        backstory="""Você é um especialista em produtos financeiros da InfinitePay e 
        também tem acesso a informações atualizadas da internet.
        
        Para perguntas sobre InfinitePay (maquininhas, taxas, Pix, conta, etc):
        - Use a ferramenta de busca no conhecimento InfinitePay
        - Fundamente suas respostas nas informações encontradas
        - Cite as fontes
        
        Para perguntas gerais (notícias, esportes, eventos):
        - Use a busca na web
        - Sintetize as informações encontradas
        - Seja objetivo e preciso
        
        Sempre forneça respostas claras, bem estruturadas e baseadas em fontes confiáveis.""",
        tools=[rag_tool, web_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    return agent
```

#### 6.3 Customer Support Agent (src/agents/support.py)

**Responsabilidade:** Resolver problemas consultando dados do cliente

**Implementação:**

```python
"""
src/agents/support.py - Customer Support Agent
"""
from crewai import Agent
from langchain_openai import ChatOpenAI

from src.config import settings
from src.tools.support_tools import GetUserDataTool, GetRecentTransactionsTool

def create_support_agent() -> Agent:
    """
    Cria o Customer Support Agent
    
    Responsável por resolver problemas de clientes consultando seus dados
    """
    llm = ChatOpenAI(
        model=settings.default_model,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
        openai_api_key=settings.openai_api_key
    )
    
    # Instanciar tools
    user_data_tool = GetUserDataTool()
    transactions_tool = GetRecentTransactionsTool()
    
    agent = Agent(
        role="Especialista em Suporte ao Cliente",
        goal="""Resolver problemas técnicos e operacionais de clientes consultando 
        seus dados e histórico para diagnosticar issues e fornecer soluções""",
        backstory="""Você é um especialista em suporte técnico com acesso aos dados 
        dos clientes da InfinitePay.
        
        Você pode:
        - Consultar informações do cliente (nome, email, status da conta, plano)
        - Ver histórico de transações recentes
        - Diagnosticar problemas baseado nos dados
        
        Quando um cliente relata um problema:
        1. Consulte os dados dele primeiro
        2. Analise o histórico de transações se relevante
        3. Diagnostique o problema
        4. Forneça uma solução clara e acionável
        
        Seja empático, profissional e objetivo. Personalize as respostas com base nos 
        dados reais do cliente.""",
        tools=[user_data_tool, transactions_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    return agent
```

---

### 7. Crew Manager (src/crew/manager.py)

**Responsabilidade:** Orquestrar os agentes usando CrewAI com **suporte a colaboração multi-agent**

#### 🔥 Estratégia de Implementação Multi-Agent

O CrewAI suporta **context sharing** entre Tasks através do parâmetro `context` e sistema de memória. A arquitetura será:

1. **Router Task:** Classifica e decide se precisa de 1 ou múltiplos agentes
2. **Agent Task(s):** Executam sequencialmente, compartilhando contexto
3. **Output consolidado:** Resposta final agregada

**Classes de complexidade:**
- **Classe A (Single):** 1 agente resolve sozinho
- **Classe B (Sequential):** Agente A → contexto → Agente B (única opção implementada)

**Como funciona Context Sharing no CrewAI:**

```python
# Task 1 - gera contexto
task1 = Task(
    description="Buscar dados do cliente",
    agent=support_agent,
    expected_output="Perfil do cliente em JSON"
)

# Task 2 - usa contexto da Task 1
task2 = Task(
    description="Recomendar produto baseado no perfil",
    agent=knowledge_agent,
    expected_output="Recomendação personalizada",
    context=[task1]  # ← Task 2 recebe output de Task 1 automaticamente
)

# Crew com memória ativa
crew = Crew(
    agents=[support_agent, knowledge_agent],
    tasks=[task1, task2],
    process=Process.sequential,  # ← Obrigatório para context sharing
    memory=True,  # ← Ativa sistema de memória para contexto adicional
    verbose=True
)
```

**O que acontece internamente:**
1. Task 1 executa e gera output (string)
2. CrewAI adiciona output de Task 1 ao contexto de Task 2
3. LLM da Task 2 recebe: `[contexto original] + [output da Task 1]`
4. Task 2 pode referenciar informações da Task 1 na resposta

**Implementação:**

```python
"""
src/crew/manager.py - CrewAI Orchestration com Multi-Agent Support
"""
from crewai import Crew, Task, Process
from typing import Dict, List
import logging
import json

from src.agents.router import create_router_agent
from src.agents.knowledge import create_knowledge_agent
from src.agents.support import create_support_agent

logger = logging.getLogger(__name__)

class AgentSwarmManager:
    """Gerenciador do agent swarm usando CrewAI com colaboração multi-agent"""
    
    def __init__(self):
        """Inicializa os agentes"""
        logger.info("Inicializando Agent Swarm...")
        
        self.router = create_router_agent()
        self.knowledge = create_knowledge_agent()
        self.support = create_support_agent()
        
        logger.info("Agentes criados com sucesso")
    
    def process_message(self, message: str, user_id: str) -> Dict:
        """
        Processa mensagem através do swarm com suporte a multi-agent
        
        Fluxo:
        1. Router classifica a mensagem e determina estratégia
        2. Executa single-agent OU multi-agent sequencial
        3. Retorna resposta + metadata
        
        Args:
            message: Mensagem do usuário
            user_id: ID do usuário
            
        Returns:
            Dict com response, agent_used, sources
        """
        logger.info(f"Processando: '{message[:50]}...' (user: {user_id})")
        
        # ETAPA 1: Roteamento Inteligente
        route_task = Task(
            description=f"""Analise esta mensagem do usuário {user_id}:

"{message}"

Classifique e determine a estratégia:

**Categorias:**
- INFINITEPAY_PRODUCT: pergunta sobre produtos/serviços InfinitePay
- CUSTOMER_SUPPORT: problema técnico ou operacional do cliente
- GENERAL_QUESTION: pergunta geral não relacionada
- PERSONALIZED_RECOMMENDATION: pergunta que combina dados do cliente + conhecimento de produtos
- TROUBLESHOOTING_ADVANCED: problema que requer dados do cliente + políticas/regras

Retorne no formato JSON:
{{
  "category": "CATEGORIA",
  "strategy": "single" ou "multi_agent",
  "agents_needed": ["agent1", "agent2"],
  "reasoning": "breve justificativa"
}}""",
            agent=self.router,
            expected_output="JSON com category, strategy, agents_needed"
        )
        
        # Executar roteamento
        route_crew = Crew(
            agents=[self.router],
            tasks=[route_task],
            process=Process.sequential,
            verbose=False
        )
        
        route_result = str(route_crew.kickoff())
        routing_decision = self._parse_routing_decision(route_result)
        
        logger.info(f"Estratégia: {routing_decision['strategy']} - Agentes: {routing_decision['agents_needed']}")
        
        # ETAPA 2: Executar estratégia
        if routing_decision['strategy'] == 'single':
            return self._execute_single_agent(message, user_id, routing_decision)
        else:
            return self._execute_multi_agent(message, user_id, routing_decision)
    
    def _execute_single_agent(self, message: str, user_id: str, decision: Dict) -> Dict:
        """Executa fluxo com um único agente"""
        category = decision['category']
        
        if category == "INFINITEPAY_PRODUCT":
            agent = self.knowledge
            agent_name = "Knowledge Agent (RAG)"
            task_desc = f"""Use a ferramenta de busca no conhecimento InfinitePay para responder:

"{message}"

Busque informações relevantes e forneça uma resposta completa e precisa.
Cite as fontes."""
            
        elif category == "GENERAL_QUESTION":
            agent = self.knowledge
            agent_name = "Knowledge Agent (Web Search)"
            task_desc = f"""Use a busca na web para responder:

"{message}"

Sintetize informações atualizadas de forma objetiva."""
            
        else:  # CUSTOMER_SUPPORT
            agent = self.support
            agent_name = "Customer Support Agent"
            task_desc = f"""Cliente {user_id} reporta:

"{message}"

1. Consulte dados do cliente
2. Verifique transações se relevante
3. Diagnostique e forneça solução clara"""
        
        # Executar
        task = Task(description=task_desc, agent=agent, expected_output="Resposta completa")
        crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
        response = crew.kickoff()
        
        sources = self._extract_sources(str(response), category)
        
        return {
            "response": str(response),
            "agent_used": agent_name,
            "sources": sources
        }
    
    def _execute_multi_agent(self, message: str, user_id: str, decision: Dict) -> Dict:
        """
        Executa fluxo colaborativo com múltiplos agentes
        
        Estratégia: Sequential Tasks com context sharing
        Task 1 → output usado como input de Task 2 → synthesis
        """
        logger.info("Executando fluxo multi-agent colaborativo")
        
        agents_needed = decision['agents_needed']
        tasks = []
        agents_list = []
        
        # TASK 1: Primeiro agente (geralmente Support para contexto)
        if 'support' in agents_needed:
            task1 = Task(
                description=f"""Analise o contexto do cliente {user_id} relevante para:

"{message}"

Busque:
- Dados do cliente (perfil, plano, status)
- Transações recentes se relevante
- Qualquer informação que ajude a personalizar a resposta

Retorne um resumo estruturado do contexto do cliente.""",
                agent=self.support,
                expected_output="Contexto estruturado do cliente"
            )
            tasks.append(task1)
            agents_list.append(self.support)
        
        # TASK 2: Knowledge Agent (usa contexto da Task 1)
        if 'knowledge' in agents_needed:
            task2 = Task(
                description=f"""Usando o contexto do cliente fornecido pela task anterior, responda:

"{message}"

Use a ferramenta RAG para buscar informações sobre produtos/serviços InfinitePay.
Personalize a resposta baseado no contexto do cliente.
Seja específico e relevante.""",
                agent=self.knowledge,
                expected_output="Resposta informada pelo contexto do cliente",
                context=[tasks[0]] if tasks else None  # Context sharing!
            )
            tasks.append(task2)
            agents_list.append(self.knowledge)
        
        # Executar crew com tasks sequenciais
        crew = Crew(
            agents=agents_list,
            tasks=tasks,
            process=Process.sequential,  # Importante: sequencial para context flow
            verbose=True
        )
        
        result = crew.kickoff()
        
        # A resposta final é o output da última task
        sources = self._extract_sources(str(result), "multi_agent")
        
        return {
            "response": str(result),
            "agent_used": "Multi-Agent Collaboration (Support + Knowledge)",
            "sources": sources
        }
    
    def _parse_routing_decision(self, route_result: str) -> Dict:
        """
        Parse do resultado do router para extrair decisão de roteamento
        
        Tenta parsear JSON, faz fallback para parsing heurístico
        """
        try:
            # Tentar parsear JSON diretamente
            import re
            json_match = re.search(r'\{[^}]+\}', route_result, re.DOTALL)
            if json_match:
                decision = json.loads(json_match.group())
                return decision
        except:
            pass
        
        # Fallback: heurística baseada em keywords
        result_upper = route_result.upper()
        
        # Detectar se precisa de múltiplos agentes
        multi_keywords = ["PERSONALIZED", "RECOMMENDATION", "ADVANCED", "TROUBLESHOOTING", 
                         "PERFIL", "MEU NEGÓCIO", "ADEQUADO PARA MIM"]
        needs_multi = any(kw in result_upper for kw in multi_keywords)
        
        # Determinar categoria
        if "INFINITEPAY_PRODUCT" in result_upper:
            category = "INFINITEPAY_PRODUCT"
            agents = ["knowledge"]
        elif "CUSTOMER_SUPPORT" in result_upper:
            category = "CUSTOMER_SUPPORT"
            agents = ["support"]
        elif "GENERAL_QUESTION" in result_upper:
            category = "GENERAL_QUESTION"
            agents = ["knowledge"]
        else:
            category = "GENERAL_QUESTION"
            agents = ["knowledge"]
        
        # Se detectou necessidade multi-agent, adicionar ambos
        if needs_multi:
            strategy = "multi_agent"
            agents = ["support", "knowledge"]
        else:
            strategy = "single"
        
        return {
            "category": category,
            "strategy": strategy,
            "agents_needed": agents,
            "reasoning": "Parsed from router output"
        }
    
    def _extract_sources(self, response: str, category: str) -> List[str]:
        """Extrai sources da resposta (implementação básica com regex)"""
        import re
        sources = []
        
        # Extrair URLs mencionadas
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, response)
        sources.extend(urls)
        
        # Se não encontrou URLs mas é sobre InfinitePay, adicionar genérico
        if not sources and "infinitepay" in response.lower():
            sources.append("https://www.infinitepay.io")
        
        # Se usou dados do cliente
        if "user_data" in category.lower() or "transaction" in response.lower():
            sources.append("customer_database")
        
        return list(set(sources))  # Remove duplicatas
```

---

### 8. Mock Database Setup

#### Script de Seed (scripts/seed_db.py)

**Responsabilidade:** Popular SQLite com dados fake

**Implementação:**

```python
"""
scripts/seed_db.py - Popular banco SQLite com dados mock
"""
import sqlite3
from datetime import datetime, timedelta
import random
from pathlib import Path

# Configuração
DB_PATH = "./data/customers.db"

def create_tables(conn):
    """Cria tabelas se não existirem"""
    cursor = conn.cursor()
    
    # Tabela users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            account_status TEXT NOT NULL,
            plan TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    # Tabela transactions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    conn.commit()

def seed_users(conn):
    """Adiciona usuários fake - INCLUI client789 para testes obrigatórios"""
    cursor = conn.cursor()
    
    users = [
        # ⚠️ OBRIGATÓRIO: client789 é usado nos cenários de teste da proposta
        ("client789", "João Silva - Restaurante", "joao.silva@email.com", "active", "premium", "2023-01-15"),
        ("user001", "Maria Santos - Loja de Roupas", "maria.santos@email.com", "active", "basic", "2023-03-20"),
        ("user002", "Pedro Oliveira - Bar", "pedro.oliveira@email.com", "blocked", "premium", "2023-02-10"),
        ("user003", "Ana Costa - E-commerce", "ana.costa@email.com", "active", "enterprise", "2023-04-05"),
        ("user004", "Carlos Ferreira - Freelancer", "carlos.ferreira@email.com", "pending", "basic", "2024-01-01"),
        ("user005", "Lucia Almeida - Salão de Beleza", "lucia.almeida@email.com", "active", "premium", "2023-06-15"),
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO users (user_id, name, email, account_status, plan, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, users)
    
    conn.commit()
    print(f"✅ {len(users)} usuários inseridos")

def seed_transactions(conn):
    """Adiciona transações fake"""
    cursor = conn.cursor()
    
    user_ids = ["client789", "user001", "user002", "user003", "user004", "user005"]
    types = ["credit", "debit", "pix", "boleto"]
    statuses = ["completed", "pending", "failed"]
    
    transactions = []
    
    for i in range(50):
        user_id = random.choice(user_ids)
        amount = round(random.uniform(10.0, 500.0), 2)
        tx_type = random.choice(types)
        status = random.choice(statuses)
        
        # Data aleatória nos últimos 30 dias
        days_ago = random.randint(0, 30)
        created_at = (datetime.now() - timedelta(days=days_ago)).isoformat()
        
        transaction_id = f"tx_{i:04d}"
        
        transactions.append((
            transaction_id,
            user_id,
            amount,
            tx_type,
            status,
            created_at
        ))
    
    cursor.executemany("""
        INSERT OR REPLACE INTO transactions 
        (transaction_id, user_id, amount, type, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, transactions)
    
    conn.commit()
    print(f"✅ {len(transactions)} transações inseridas")

def seed_if_empty():
    """
    Verifica se banco está vazio e popula se necessário
    
    Chamado automaticamente no startup da aplicação
    """
    # Criar diretório data se não existir
    Path("./data").mkdir(exist_ok=True)
    
    # Conectar ao banco
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Criar tabelas se não existirem
    create_tables(conn)
    
    # Verificar se já tem dados
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"✅ Banco já populado com {count} usuários")
        conn.close()
        return
    
    print("🌱 Banco vazio, populando...")
    seed_users(conn)
    seed_transactions(conn)
    conn.close()
    print("✅ Seed completo!")

def main():
    """Executa o seed (uso manual)"""
    print("🌱 Iniciando seed do banco de dados...")
    
    # Criar diretório data se não existir
    Path("./data").mkdir(exist_ok=True)
    
    # Conectar ao banco
    conn = sqlite3.connect(DB_PATH)
    
    # Criar tabelas
    create_tables(conn)
    print("✅ Tabelas criadas")
    
    # Seed
    seed_users(conn)
    seed_transactions(conn)
    
    conn.close()
    print("✅ Seed completo!")

if __name__ == "__main__":
    main()
```

---

## 📅 Cronograma de 10 Dias Detalhado

### DIA 1: Terça (14/01) - Setup Inicial [4-5h]

**Objetivo:** Estrutura base funcionando

#### Task 1.1: Estrutura de Pastas [30min]
```bash
mkdir -p src/{agents,crew,rag,tools}
mkdir -p scripts tests data docs
touch src/__init__.py src/{agents,crew,rag,tools}/__init__.py
```

#### Task 1.2: Arquivos de Configuração [1h]
- [ ] `requirements.txt`
- [ ] `.gitignore`
- [ ] `.env.example`
- [ ] `src/config.py`
- [ ] `src/schemas.py`

**Teste:** Importar config e schemas sem erro

#### Task 1.3: FastAPI Hello World [1.5h]
- [ ] `src/main.py` básico
- [ ] Endpoint `/health`
- [ ] Rodar local: `uvicorn src.main:app --reload`

**Teste:** `curl localhost:8000/health` retorna 200

#### Task 1.4: SQLite Mock Database [1.5h]
- [ ] `scripts/seed_db.py`
- [ ] Rodar seed: `python scripts/seed_db.py`
- [ ] Verificar no DB Browser

**Teste:** Query manual retorna dados

---

### DIA 2: Quarta (15/01) - RAG Ingestion [5-6h]

**Objetivo:** ChromaDB populado com docs InfinitePay

**⚠️ DECISÃO TÉCNICA - CHUNKING STRATEGY:**

Baseado em análise HTML das páginas InfinitePay (executada 14/01):
- **Score médio:** 3.7/5.0
- **Estrutura:** Headers bem definidos (H2/H3), 600-900 seções por página
- **Keywords:** Abundantes (taxa: 15-43x, %: 8-34x por página)
- **Problema:** Sem tabelas, informações de taxas em divs/parágrafos

**✅ ESTRATÉGIA ESCOLHIDA: Chunking Semântico por Seção HTML**

**Método Híbrido:**
1. Parse HTML por headers (H2/H3)
2. Cada seção = 1 chunk candidato
3. Se chunk > 2000 chars → quebrar com overlap 400
4. Se chunk < 300 chars → juntar com próxima seção
5. Metadata enriquecida: {produto, seção, header_text}

**Benefícios:** +20-30% qualidade, taxas mantêm contexto de produto
**Tempo extra:** +2h (justificado pelo score 3.7/5)

---

#### Task 2.1: URLs e Estrutura RAG [1h]
- [ ] `src/rag/urls.py`
- [ ] `src/rag/__init__.py`
- [ ] Criar diretório `data/chromadb/`

#### Task 2.2: Ingestão Pipeline [3-4h]
- [ ] `src/rag/ingest.py`
  - WebBaseLoader
  - RecursiveCharacterTextSplitter
  - OpenAI Embeddings
  - ChromaDB storage
- [ ] Função `ingest_if_empty()`

**Teste:** Rodar script standalone
```python
python -c "from src.rag.ingest import ingest_documents; ingest_documents()"
```

Verificar:
- [ ] `data/chromadb/` criado
- [ ] Logs mostram N chunks inseridos
- [ ] Sem erros

#### Task 2.3: Search/Retrieval [1.5h]
- [ ] `src/rag/search.py`
- [ ] Classe `RAGSearcher`
- [ ] Métodos `search()` e `format_context()`

**Teste:** Query manual
```python
from src.rag.search import RAGSearcher
searcher = RAGSearcher()
results = searcher.search("taxas maquininha")
print(results)
```

---

### DIA 3: Quinta (16/01) - Tools [4-5h]

**Objetivo:** Todas as tools funcionando

#### Task 3.1: RAG Tool [1.5h]
- [ ] `src/tools/rag_tool.py`
- [ ] Wrapper CrewAI Tool
- [ ] Input schema
- [ ] Descrição clara

**Teste:** Instanciar e chamar manualmente
```python
from src.tools.rag_tool import RAGSearchTool
tool = RAGSearchTool()
result = tool._run("taxas da maquininha smart")
print(result)
```

#### Task 3.2: Web Search Tool [1.5h]
- [ ] `src/tools/web_tool.py`
- [ ] DuckDuckGo integration
- [ ] Wrapper CrewAI Tool

**Teste:**
```python
from src.tools.web_tool import WebSearchTool
tool = WebSearchTool()
result = tool._run("Palmeiras último jogo")
print(result)
```

#### Task 3.3: Support Tools [2h]
- [ ] `src/tools/support_tools.py`
- [ ] `GetUserDataTool`
- [ ] `GetRecentTransactionsTool`

**Teste:**
```python
from src.tools.support_tools import GetUserDataTool, GetRecentTransactionsTool

user_tool = GetUserDataTool()
print(user_tool._run("client789"))

tx_tool = GetRecentTransactionsTool()
print(tx_tool._run("client789"))
```

---

### DIA 4: Sexta (17/01) - Router Agent [3-4h]

**Objetivo:** Router classificando corretamente

#### Task 4.1: Router Agent [2h]
- [ ] `src/agents/router.py`
- [ ] Função `create_router_agent()`
- [ ] Role, goal, backstory bem definidos
- [ ] LLM configurado

#### Task 4.2: Testes de Classificação [1.5h]

**⚠️ IMPORTANTE:** Router deve detectar quando precisa de múltiplos agentes!

Criar script `scripts/test_router.py`:
```python
from crewai import Crew, Task, Process
from src.agents.router import create_router_agent

router = create_router_agent()

test_messages = [
    # Single agent
    ("Quais as taxas da maquininha?", "single", ["knowledge"]),
    ("Quando foi o jogo do Palmeiras?", "single", ["knowledge"]),
    ("Não consigo fazer login", "single", ["support"]),
    
    # Multi-agent (IMPORTANTE!)
    ("Qual maquininha é melhor para meu negócio?", "multi_agent", ["support", "knowledge"]),
    ("Minha transação Pix falhou, o que houve?", "multi_agent", ["support", "knowledge"]),
    ("Como funciona Pix parcelado e posso usar?", "multi_agent", ["support", "knowledge"]),
]

for msg, expected_strategy, expected_agents in test_messages:
    task = Task(
        description=f"""Analise: "{msg}"
        
Retorne JSON:
{{"category": "...", "strategy": "single|multi_agent", "agents_needed": [...]}}""",
        agent=router,
        expected_output="JSON estruturado"
    )
    crew = Crew(agents=[router], tasks=[task], process=Process.sequential)
    result = crew.kickoff()
    print(f"{msg}")
    print(f"  Esperado: {expected_strategy} - {expected_agents}")
    print(f"  Resultado: {result}\n")
```

**Teste:** Verificar que router identifica corretamente cenários multi-agent!

---

### DIA 5-6: Sábado/Domingo (18-19/01) - AGENTES + CREW [12-16h total]

**Objetivo:** Sistema completo funcionando end-to-end

#### Sábado - Agentes [6-8h]

**Task 5.1: Knowledge Agent [3h]**
- [ ] `src/agents/knowledge.py`
- [ ] Função `create_knowledge_agent()`
- [ ] Integrar RAG Tool e Web Tool
- [ ] Role, goal, backstory

**Teste:** Testar agent isoladamente
```python
from crewai import Crew, Task, Process
from src.agents.knowledge import create_knowledge_agent

knowledge = create_knowledge_agent()

task = Task(
    description="Use RAG para responder: Quais as taxas da maquininha smart?",
    agent=knowledge,
    expected_output="Resposta completa"
)

crew = Crew(agents=[knowledge], tasks=[task], process=Process.sequential)
result = crew.kickoff()
print(result)
```

**Task 5.2: Support Agent [3h]**
- [ ] `src/agents/support.py`
- [ ] Função `create_support_agent()`
- [ ] Integrar Support Tools
- [ ] Role, goal, backstory

**Teste:** Testar agent isoladamente
```python
from crewai import Crew, Task, Process
from src.agents.support import create_support_agent

support = create_support_agent()

task = Task(
    description="Cliente client789 não consegue fazer transferências. Investigue.",
    agent=support,
    expected_output="Diagnóstico e solução"
)

crew = Crew(agents=[support], tasks=[task], process=Process.sequential)
result = crew.kickoff()
print(result)
```

#### Domingo - Crew Integration [6-8h]

**Task 6.1: Crew Manager [4h]**
- [ ] `src/crew/manager.py`
- [ ] Classe `AgentSwarmManager`
- [ ] Método `process_message()`
- [ ] Lógica de roteamento + execução

**Task 6.2: Integração FastAPI [2h]**
- [ ] Atualizar `src/main.py`
- [ ] Endpoint `/chat` completo
- [ ] Lifespan events (startup ingest)
- [ ] Error handling

**Task 6.3: Teste End-to-End [2h]**
Rodar aplicação:
```bash
uvicorn src.main:app --reload
```

Testar todas as mensagens:
```bash
# InfinitePay product
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Quais as taxas da maquininha smart?", "user_id": "client789"}'

# General question
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Quando foi o último jogo do Palmeiras?", "user_id": "client789"}'

# Customer support
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Por que não consigo fazer transferências?", "user_id": "client789"}'
```

---

### DIA 7: Segunda (20/01) - Refinamento [4-5h]

**Objetivo:** Sistema robusto e polido

#### Task 7.1: Error Handling [1.5h]
- [ ] Try/catch em todos os endpoints
- [ ] HTTP exceptions apropriadas
- [ ] Mensagens de erro user-friendly

#### Task 7.2: Logging [1h]
- [ ] Logs estruturados
- [ ] INFO para operações normais
- [ ] ERROR para problemas
- [ ] Timestamps

#### Task 7.3: Sources no Response [1h]
- [ ] Melhorar extração de sources
- [ ] Retornar URLs usadas pelo RAG
- [ ] Incluir no ChatResponse

#### Task 7.4: Validações [1h]
- [ ] Validar user_id não vazio
- [ ] Mensagem min_length
- [ ] Timeout de 60s para LLM calls

**Teste:** Testar edge cases

---

### DIA 8: Terça (21/01) - Docker + Testes [5-6h]

**Objetivo:** Aplicação containerizada e testes básicos

#### Task 8.1: Dockerfile [2h]
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY src/ src/
COPY scripts/ scripts/

# Create data directory
RUN mkdir -p data

# Expose port
EXPOSE 8000

# Run app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Teste:**
```bash
docker build -t cloudwalk-agent-swarm .
docker run -p 8000:8000 --env-file .env cloudwalk-agent-swarm
```

#### Task 8.2: docker-compose.yml [1h]
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    env_file:
      - .env
    environment:
      - ENVIRONMENT=production
```

**Teste:**
```bash
docker-compose up
```

#### Task 8.3: Testes Pytest [2-3h]

**test_api.py:**
```python
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200

def test_chat_endpoint():
    response = client.post("/chat", json={
        "message": "Teste",
        "user_id": "test_user"
    })
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "agent_used" in data
```

**test_rag.py:**
```python
from src.rag.search import RAGSearcher

def test_rag_search():
    searcher = RAGSearcher()
    results = searcher.search("maquininha")
    assert len(results) > 0
    assert 'content' in results[0]
```

**Rodar:**
```bash
pytest tests/ -v
```

---

### DIA 9: Quarta (22/01) - Documentação [5-6h]

**Objetivo:** README nota 10

#### Task 9.1: README - Introdução e Arquitetura [2h]
- [ ] Título e badges
- [ ] Descrição do projeto
- [ ] Diagrama de arquitetura (copiar do PRD ou criar no mermaid)
- [ ] Explicação dos 3 agentes
- [ ] Fluxo de processamento

#### Task 9.2: README - Setup e Uso [2h]
- [ ] Pré-requisitos
- [ ] Instruções de instalação
- [ ] Como configurar .env
- [ ] Como rodar com Docker
- [ ] Exemplos de curl/requests
- [ ] Mensagens de teste

#### Task 9.3: README - Decisões Técnicas [1h]
- [ ] Por que CrewAI?
- [ ] Por que ChromaDB?
- [ ] Por que DuckDuckGo?
- [ ] Stack técnica detalhada

#### Task 9.4: README - RAG e Testes [1h]
- [ ] Como funciona o RAG pipeline
- [ ] URLs indexadas
- [ ] Como rodar testes
- [ ] **Como você usou Cursor/Claude**

---

### DIA 10: Quinta (23/01) - ENTREGA [4-5h]

**Objetivo:** Projeto finalizado e submetido

#### Task 10.1: Revisão de Código [2h]
- [ ] Adicionar docstrings faltantes
- [ ] Type hints completos
- [ ] Remover código comentado
- [ ] Formatar com black
- [ ] Lint com flake8

```bash
pip install black flake8
black src/ tests/
flake8 src/ tests/
```

#### Task 10.2: TESTING_STRATEGY.md [1h]
- [ ] Criar `docs/TESTING_STRATEGY.md`
- [ ] Testes implementados
- [ ] Como expandir
- [ ] Integration tests
- [ ] Performance testing

#### Task 10.3: Teste Final E2E [1h]
- [ ] Derrubar tudo
- [ ] Deletar data/
- [ ] Rebuild do zero
- [ ] Seguir README
- [ ] Testar TODAS as 8 mensagens do desafio

#### Task 10.4: Git e Submissão [30min]
- [ ] Commits bem organizados
- [ ] .gitignore correto
- [ ] Push para GitHub
- [ ] README renderizando bem
- [ ] Submeter para CloudWalk

---

## 🧪 Cenários de Teste Completos

### ⚠️ IMPORTANTE: Incluir Testes Multi-Agent

Além das 8 mensagens obrigatórias do desafio, você DEVE testar cenários que requerem **colaboração entre agentes** (conforme linha 19 da proposta: "sequence of agents").

### Mensagens Obrigatórias do Desafio

#### Categoria: InfinitePay Products (Knowledge + RAG - Single Agent)

**1. Taxas da Maquininha Smart**
```json
{
  "message": "What are the fees of the Maquininha Smart",
  "user_id": "client789"
}
```
**Esperado:**
- Router classifica como INFINITEPAY_PRODUCT
- Knowledge Agent usa RAG Tool
- Resposta menciona taxas de débito/crédito
- Sources incluem URL da maquininha

**2. Custo da Maquininha**
```json
{
  "message": "What is the cost of the Maquininha Smart?",
  "user_id": "client789"
}
```
**Esperado:** Similar ao anterior

**3. Taxas de Transações**
```json
{
  "message": "What are the rates for debit and credit card transactions?",
  "user_id": "client789"
}
```
**Esperado:**
- RAG busca informações sobre taxas
- Diferencia débito vs crédito

**4. Usar Celular como Maquininha**
```json
{
  "message": "How can I use my phone as a card machine?",
  "user_id": "client789"
}
```
**Esperado:**
- RAG busca sobre tap-to-pay ou maquininha-celular
- Explica o recurso

#### Categoria: General Questions (Knowledge + Web Search)

**5. Último Jogo do Palmeiras**
```json
{
  "message": "Quando foi o último jogo do Palmeiras?",
  "user_id": "client789"
}
```
**Esperado:**
- Router classifica como GENERAL_QUESTION
- Knowledge Agent usa Web Search Tool
- Retorna informação atualizada

**6. Notícias de São Paulo**
```json
{
  "message": "Quais as principais notícias de São Paulo hoje?",
  "user_id": "client789"
}
```
**Esperado:**
- Web Search
- Resumo de notícias recentes

#### Categoria: Customer Support (Support Agent + Tools)

**7. Problema com Transferências**
```json
{
  "message": "Why I am not able to make transfers?",
  "user_id": "client789"
}
```
**Esperado:**
- Router classifica como CUSTOMER_SUPPORT
- Support Agent consulta dados do client789
- Verifica transações recentes
- Diagnostica problema (ex: conta bloqueada, limite atingido)
- Resposta personalizada

**8. Problema de Login**
```json
{
  "message": "I can't sign in to my account.",
  "user_id": "client789"
}
```
**Esperado:**
- Support Agent
- Consulta status da conta
- Sugere soluções (reset password, verificar email, etc)

---

### 🔥 Mensagens BONUS - Multi-Agent Collaboration (CRÍTICO!)

**Estes testes demonstram a arquitetura colaborativa pedida na proposta!**

#### Test 9: Recomendação Personalizada (Multi-Agent)

```json
{
  "message": "Qual maquininha da InfinitePay é melhor para meu tipo de negócio?",
  "user_id": "client789"
}
```

**Esperado:**
- ✅ Router identifica: `strategy: "multi_agent"`
- ✅ Task 1: Support Agent busca perfil do cliente (tipo negócio, volume)
- ✅ Task 2: Knowledge Agent busca informações sobre maquininhas (com contexto da Task 1)
- ✅ Resposta final **personalizada** baseada nos dados do cliente
- ✅ agent_used: "Multi-Agent Collaboration"
- ✅ sources: ["customer_database", "https://www.infinitepay.io/maquininha"]

**Exemplo de resposta esperada:**
```
"Com base no perfil do seu restaurante com volume médio de 200 transações/mês 
e ticket médio de R$ 45, recomendo a Maquininha Smart porque oferece as melhores 
taxas para esse volume (1.99% débito, 3.49% crédito) e tem conectividade estável..."
```

---

#### Test 10: Troubleshooting com Contexto (Multi-Agent)

```json
{
  "message": "Minha última transação Pix foi recusada. Por quê?",
  "user_id": "client789"
}
```

**Esperado:**
- ✅ Router identifica: `strategy: "multi_agent"`
- ✅ Task 1 (SEQUENTIAL): Support Agent busca detalhes da transação específica
- ✅ Task 2 (SEQUENTIAL com context): Knowledge Agent busca políticas/regras sobre Pix usando contexto do erro da Task 1
- ✅ Resposta diagnostica o problema específico + solução
- ✅ sources: ["transaction_logs", "https://www.infinitepay.io/pix"]

**Exemplo de resposta esperada:**
```
"Sua transação Pix de R$ 1.500 foi recusada porque excedeu o limite diário 
de R$ 1.000 do seu plano Básico. Para aumentar o limite, você pode:
1. Fazer upgrade para plano Premium (limite de R$ 5.000/dia)
2. Solicitar aumento temporário através do app..."
```

---

#### Test 11: Elegibilidade + Informação (Multi-Agent)

```json
{
  "message": "Como funciona o Pix parcelado e eu posso usar no meu plano?",
  "user_id": "user002"
}
```

**Esperado:**
- ✅ Router identifica: `strategy: "multi_agent"`
- ✅ Task 1 (SEQUENTIAL): Support Agent verifica plano do usuário (elegibilidade)
- ✅ Task 2 (SEQUENTIAL com context): Knowledge Agent explica Pix parcelado (RAG) usando info de elegibilidade
- ✅ Resposta combina: explicação técnica + status de elegibilidade do cliente
- ✅ sources: ["customer_database", "https://www.infinitepay.io/pix-parcelado"]

**Exemplo de resposta esperada:**
```
"O Pix parcelado permite que você receba pagamentos Pix em até 12x...
[explicação técnica do RAG]

Verificando seu plano Premium, você TEM acesso a este recurso! Para ativá-lo..."
```

---

#### Test 12: Contexto Financeiro + Produto (Multi-Agent)

```json
{
  "message": "Preciso de crédito para investir no negócio. Quais opções tenho?",
  "user_id": "user003"
}
```

**Esperado:**
- ✅ Task 1 (SEQUENTIAL): Support verifica histórico financeiro do cliente
- ✅ Task 2 (SEQUENTIAL com context): Knowledge busca sobre opções de empréstimo InfinitePay usando histórico
- ✅ Resposta personalizada com limite pré-aprovado (se aplicável)

---

### Validação da Arquitetura Multi-Agent

Para garantir que a arquitetura colaborativa está funcionando:

**Checklist:**
- [ ] Router consegue identificar cenários multi-agent
- [ ] Support Agent executa primeiro e gera contexto estruturado
- [ ] Knowledge Agent recebe e USA o contexto do Support
- [ ] Resposta final integra informações de ambos os agentes
- [ ] Logs mostram execução sequencial (Task 1 → Task 2)
- [ ] agent_used indica "Multi-Agent Collaboration"
- [ ] sources incluem ambas as origens (DB + RAG)

**Como testar:**
```bash
# Teste multi-agent
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Qual maquininha é melhor para meu negócio?",
    "user_id": "client789"
  }'

# Verificar nos logs:
# [INFO] Estratégia: multi_agent - Agentes: ['support', 'knowledge']
# [INFO] Executando fluxo multi-agent colaborativo
# [Agent: Customer Support Agent] Buscando perfil do cliente...
# [Agent: Knowledge Agent] Usando contexto do cliente para recomendar...
```

---

## ✅ Checklist de Qualidade Final

### Funcionalidade
- [ ] API responde em `/chat` e `/health`
- [ ] Router classifica corretamente as 3 categorias
- [ ] **Router identifica cenários multi-agent** (CRÍTICO!)
- [ ] **Router retorna JSON válido** (usando response_format json_object)
- [ ] Knowledge Agent responde sobre InfinitePay usando RAG
- [ ] Knowledge Agent responde perguntas gerais via web
- [ ] Support Agent acessa dados mock do user_id
- [ ] **Multi-agent collaboration funciona** (context sharing SEQUENTIAL entre agents)
- [ ] **Banco SQLite é populado automaticamente no startup**
- [ ] **client789 existe no banco** (obrigatório para testes)
- [ ] Todas as 8 mensagens obrigatórias funcionam
- [ ] **Pelo menos 2 cenários multi-agent testados e funcionando** (sempre sequential)
- [ ] Respostas são relevantes e úteis
- [ ] Respostas multi-agent são personalizadas com dados do cliente

### Código
- [ ] Estrutura modular e organizada
- [ ] Type hints em todas as funções
- [ ] Docstrings nas classes/funções principais
- [ ] Nomes de variáveis claros e descritivos
- [ ] Sem código comentado ou debug prints
- [ ] Error handling robusto
- [ ] Logging adequado

### RAG Pipeline
- [ ] Scraping das 13 URLs funciona
- [ ] Chunking com overlap apropriado
- [ ] Embeddings gerados corretamente
- [ ] ChromaDB persiste em disco
- [ ] Retrieval retorna chunks relevantes
- [ ] Ingestão automática no startup

### Docker
- [ ] `docker-compose up` funciona na primeira vez
- [ ] Dados persistem no volume
- [ ] .env é carregado corretamente
- [ ] Build sem warnings críticos
- [ ] Imagem otimizada (não muito grande)

### Testes
- [ ] Testes básicos implementados
- [ ] Todos os testes passam (`pytest`)
- [ ] Fixtures configurados corretamente
- [ ] Estratégia de testes documentada

### Documentação
- [ ] README completo e claro
- [ ] Instruções de setup testadas
- [ ] Exemplos de uso funcionais
- [ ] Arquitetura bem explicada
- [ ] Design decisions justificadas
- [ ] RAG pipeline explicado
- [ ] Uso de IA documentado
- [ ] .env.example completo

### Git
- [ ] .gitignore correto (não commita .env, data/)
- [ ] Commits organizados e descritivos
- [ ] README renderiza bem no GitHub
- [ ] Sem arquivos desnecessários

---

## 🤖 Guia de Desenvolvimento com Cursor

### Estratégia Geral

**Princípio:** Desenvolver incrementalmente, testando cada componente isoladamente antes de integrar.

### Como Usar o Cursor Efetivamente

#### 1. Contexto é Rei

Antes de pedir para o Cursor implementar algo:

```
@PRD.md Seguindo o PRD, vou implementar [COMPONENTE].

Contexto:
- Stack: Python + FastAPI + CrewAI
- Objetivo: [descrição breve]
- Dependências: [arquivos relacionados]

Implemente [COMPONENTE] conforme especificado no PRD.
```

#### 2. Prompts Específicos e Granulares

**❌ Ruim:**
"Crie o sistema de agentes"

**✅ Bom:**
"Implemente a função create_knowledge_agent() em src/agents/knowledge.py.
O agente deve ter:
- Role: Especialista em Conhecimento
- Tools: RAG Tool e Web Search Tool
- LLM: GPT-3.5-turbo
- Seguir o template do PRD"

#### 3. Desenvolvimento Incremental

**Sequência recomendada:**

```
Sessão 1: Setup
├── requirements.txt
├── .gitignore
├── .env.example
└── src/config.py

Sessão 2: Schemas e FastAPI básico
├── src/schemas.py
└── src/main.py (hello world)

Sessão 3: SQLite Mock
└── scripts/seed_db.py

Sessão 4: RAG Ingestão
├── src/rag/urls.py
└── src/rag/ingest.py

... e assim por diante
```

#### 4. Teste Imediatamente

Após cada implementação:

```python
# Criar scripts de teste rápidos
# scripts/test_component.py

from src.component import ComponentClass

component = ComponentClass()
result = component.method()
print(result)
```

#### 5. Use o Composer para Iteração

Se algo não funcionar:

```
O componente X está retornando erro Y.

Erro:
[cole o traceback]

Debug:
1. Verifique se [possível causa]
2. Ajuste [sugestão]
3. Teste novamente
```

#### 6. Aproveite Multi-file Editing

```
Preciso integrar o RAG Tool no Knowledge Agent.

Arquivos envolvidos:
- @src/tools/rag_tool.py (já existe)
- @src/agents/knowledge.py (adicionar tool)

Integre o RAG Tool como tool do Knowledge Agent.
```

### Prompts Úteis por Etapa

#### Setup Inicial
```
Crie a estrutura de pastas completa para o projeto CloudWalk Agent Swarm conforme o PRD.
Use Python 3.11, FastAPI, CrewAI.
```

#### Configurações
```
Implemente src/config.py usando pydantic-settings para carregar variáveis do .env.
Variáveis necessárias: [listar conforme PRD]
```

#### RAG Ingestão
```
Implemente o pipeline de ingestão RAG em src/rag/ingest.py:
1. Scraping com WebBaseLoader (13 URLs)
2. Chunking com RecursiveCharacterTextSplitter
3. Embeddings com OpenAI
4. Storage em ChromaDB persistente

Inclua função ingest_if_empty() que verifica se já foi ingerido.
```

#### CrewAI Agent
```
Crie o Knowledge Agent em src/agents/knowledge.py.

Especificação:
- Role: Especialista em Conhecimento
- Goal: Responder perguntas usando RAG ou Web Search
- Tools: RAG Tool e Web Search Tool
- Backstory: [conforme PRD]

Use ChatOpenAI com settings.default_model.
```

#### Debugging
```
O endpoint /chat está retornando 500.

Erro: [cole erro]

Análise:
1. Verifique se Crew Manager está inicializado
2. Confira se tools estão instanciadas corretamente
3. Adicione try/catch para capturar exceções específicas

Corrija o problema.
```

### Documentando Uso da IA

No README, adicione seção:

```markdown
## Desenvolvimento com IA

Este projeto foi desenvolvido utilizando assistência de IA (Claude 3.5 Sonnet via Cursor).

### Como a IA foi utilizada:

1. **Estruturação:** PRD completo gerado com especificações detalhadas
2. **Implementação:** Código gerado incrementalmente, componente por componente
3. **Debugging:** Assistência em resolver erros e otimizar código
4. **Documentação:** Geração de docstrings e README

### Partes geradas por IA vs. Humanas:

**Humano (Você):**
- Arquitetura geral e decisões técnicas
- Escolha de stack (CrewAI, ChromaDB, etc)
- Prompts e instruções específicas
- Lógica de roteamento e fluxo
- Teste e validação
- Refinamentos e ajustes

**IA (Cursor/Claude):**
- Código boilerplate
- Implementação de funções específicas
- Docstrings e comentários
- Estrutura de testes
- README sections

### Vantagens:
- Desenvolvimento 3-4x mais rápido
- Código consistente e bem documentado
- Foco em arquitetura ao invés de sintaxe
- Debugging assistido

### Limitações:
- Necessário entender o código gerado
- Revisão crítica de decisões da IA
- Testes manuais ainda essenciais
```

---

## 📊 Métricas de Sucesso

### Técnicas
- [ ] Latência média < 5s por request
- [ ] Taxa de erro < 5%
- [ ] ChromaDB carrega em < 10s
- [ ] Build Docker < 5min

### Qualitativas
- [ ] Código legível e manutenível
- [ ] README claro e completo
- [ ] Arquitetura bem explicada
- [ ] Demonstra domínio de AI agents

---

## 🎯 Entrega Final

### O que submeter:

1. **Repositório GitHub** com:
   - Código completo
   - README.md
   - Dockerfile e docker-compose.yml
   - .env.example
   - Tests

2. **Instruções claras** de:
   - Como configurar
   - Como rodar
   - Como testar

3. **Documentação** de:
   - Arquitetura
   - Decisões técnicas
   - Uso de LLMs no desenvolvimento

### Como impressionar:

✅ **FAZER:**
- Código limpo e bem organizado
- Documentação excelente
- Testes funcionais
- Docker funciona de primeira
- README com diagramas
- Explicar decisões técnicas

❌ **NÃO FAZER:**
- Código desorganizado
- Commits bagunçados ("fix", "test", "asdf")
- README genérico
- Docker com problemas
- Falta de testes
- Sem explicar por quê escolheu X ou Y

---

## 🚀 Conclusão

Este PRD é seu **guia completo** para desenvolver o projeto CloudWalk Agent Swarm em 10 dias.

### Próximos Passos:

1. **Ler este PRD completamente** (você está aqui ✅)
2. **Criar repositório GitHub**
3. **Seguir cronograma dia-a-dia**
4. **Testar incrementalmente**
5. **Documentar durante o desenvolvimento**
6. **Entregar com confiança**

### Lembre-se:

- **Qualidade > Velocidade:** Melhor entregar algo bem feito que incompleto
- **Teste continuamente:** Não deixe para testar tudo no final
- **Documente enquanto desenvolve:** README vai sendo construído junto
- **Use o Cursor inteligentemente:** Prompts específicos, contexto claro
- **Peça ajuda quando travar:** Debugging é parte do processo

**Você consegue! 🎯**

Este é um projeto desafiador mas totalmente viável em 10 dias com dedicação e o uso inteligente das ferramentas (Cursor + este PRD).

Boa sorte, Caio! 🚀

---

**Versão:** 1.0  
**Data:** 13 de Janeiro de 2026  
**Autor:** Caio + Claude (PRD gerado via Cursor)

