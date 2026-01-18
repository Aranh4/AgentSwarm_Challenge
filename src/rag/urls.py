"""
InfinitePay URLs for RAG Pipeline ingestion

Total: 18 URLs (core products and services + alternatives)
"""

INFINITEPAY_URLS = [
    "https://www.infinitepay.io",
    "https://www.infinitepay.io/taxas",  # IMPORTANT: Page with exact fee percentages
    "https://www.infinitepay.io/maquininha",
    "https://www.infinitepay.io/maquininha-celular",
    "https://www.infinitepay.io/tap-to-pay",
    "https://www.infinitepay.io/pdv",
    "https://www.infinitepay.io/receba-na-hora",
    "https://www.infinitepay.io/gestao-de-cobranca-2",
    "https://www.infinitepay.io/gestao-de-cobranca",  # Alternative
    "https://www.infinitepay.io/link-de-pagamento",
    "https://www.infinitepay.io/loja-online",
    "https://www.infinitepay.io/boleto",
    "https://www.infinitepay.io/conta-digital",
    "https://www.infinitepay.io/conta-pj",  # Alternative
    "https://www.infinitepay.io/pix",
    "https://www.infinitepay.io/pix-parcelado",  # Alternative
    "https://www.infinitepay.io/emprestimo",
    "https://www.infinitepay.io/cartao",
    "https://www.infinitepay.io/rendimento"
]

# Total expected URLs for validation
EXPECTED_URL_COUNT = len(INFINITEPAY_URLS)

