"""Tabela de preços versionada — lê platform/pricing (doc 05 §2).

Na V1, preços hardcoded com possibilidade de override via Firestore.
Valores em USD por 1M tokens, convertidos para BRL no cálculo.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelPricing:
    """Preço por 1M tokens (USD)."""

    input_per_1m: float
    output_per_1m: float


# Preços de referência (atualizar conforme Vertex pricing)
DEFAULT_PRICING: dict[str, ModelPricing] = {
    "claude-opus-4-6": ModelPricing(input_per_1m=15.0, output_per_1m=75.0),
    "claude-sonnet-4-6": ModelPricing(input_per_1m=3.0, output_per_1m=15.0),
    "gemini-2.5-flash": ModelPricing(input_per_1m=0.15, output_per_1m=0.60),
    "gemini-2.5-pro": ModelPricing(input_per_1m=1.25, output_per_1m=10.0),
    "text-embedding-005": ModelPricing(input_per_1m=0.025, output_per_1m=0.0),
}

# Câmbio de referência (doc 05 §1): margem de 5% a favor do bloqueio
DEFAULT_CAMBIO_USD_BRL = 5.25  # atualizar 1x/dia via API de cotação


def calculate_cost_brl(
    model: str,
    tokens_in: int,
    tokens_out: int,
    cambio: float = DEFAULT_CAMBIO_USD_BRL,
) -> float:
    """Calcula custo em BRL para uma chamada LLM."""
    pricing = DEFAULT_PRICING.get(model)
    if not pricing:
        # Modelo desconhecido — usar preço conservador (Opus)
        pricing = DEFAULT_PRICING["claude-opus-4-6"]

    cost_usd = (tokens_in / 1_000_000 * pricing.input_per_1m) + (
        tokens_out / 1_000_000 * pricing.output_per_1m
    )
    return round(cost_usd * cambio, 4)
