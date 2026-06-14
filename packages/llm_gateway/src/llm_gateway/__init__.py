"""llm_gateway — wrapper único de LLM + ledger. Ninguém chama Vertex direto."""

from llm_gateway.client import LlmGateway, LlmResult
from llm_gateway.pricing import DEFAULT_CAMBIO_USD_BRL, DEFAULT_PRICING, calculate_cost_brl
from llm_gateway.routing import resolve_model

__all__ = [
    "DEFAULT_CAMBIO_USD_BRL",
    "DEFAULT_PRICING",
    "LlmGateway",
    "LlmResult",
    "calculate_cost_brl",
    "resolve_model",
]
