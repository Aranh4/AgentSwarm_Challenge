"""
URLs da InfinitePay para ingestão no RAG Pipeline

Total: 18 URLs (produtos e serviços principais + alternativas)
"""

INFINITEPAY_URLS = [
    "https://www.infinitepay.io",
    "https://www.infinitepay.io/taxas",  # IMPORTANTE: Página com % exatos das taxas
    "https://www.infinitepay.io/maquininha",
    "https://www.infinitepay.io/maquininha-celular",
    "https://www.infinitepay.io/tap-to-pay",
    "https://www.infinitepay.io/pdv",
    "https://www.infinitepay.io/receba-na-hora",
    "https://www.infinitepay.io/gestao-de-cobranca-2",
    "https://www.infinitepay.io/gestao-de-cobranca",  # Alternativa
    "https://www.infinitepay.io/link-de-pagamento",
    "https://www.infinitepay.io/loja-online",
    "https://www.infinitepay.io/boleto",
    "https://www.infinitepay.io/conta-digital",
    "https://www.infinitepay.io/conta-pj",  # Alternativa
    "https://www.infinitepay.io/pix",
    "https://www.infinitepay.io/pix-parcelado",  # Alternativa
    "https://www.infinitepay.io/emprestimo",
    "https://www.infinitepay.io/cartao",
    "https://www.infinitepay.io/rendimento"
]

# Total de URLs esperadas para validação
EXPECTED_URL_COUNT = len(INFINITEPAY_URLS)

