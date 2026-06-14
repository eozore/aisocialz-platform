"""Testes de cálculo de custo — doc 05 §2."""

from llm_gateway.pricing import calculate_cost_brl


def test_calculate_cost_opus() -> None:
    """Opus: $15/1M in + $75/1M out. Com câmbio 5.25."""
    cost = calculate_cost_brl("claude-opus-4-6", tokens_in=1000, tokens_out=500, cambio=5.25)
    # (1000/1M * 15 + 500/1M * 75) * 5.25
    # = (0.015 + 0.0375) * 5.25 = 0.0525 * 5.25 = 0.275625
    assert abs(cost - 0.2756) < 0.001


def test_calculate_cost_flash() -> None:
    """Flash: $0.15/1M in + $0.60/1M out. Muito barato."""
    cost = calculate_cost_brl("gemini-2.5-flash", tokens_in=10000, tokens_out=2000, cambio=5.0)
    # (10000/1M * 0.15 + 2000/1M * 0.60) * 5.0
    # = (0.0015 + 0.0012) * 5.0 = 0.0027 * 5.0 = 0.0135
    assert abs(cost - 0.0135) < 0.001


def test_unknown_model_uses_conservative_pricing() -> None:
    """Modelo desconhecido usa preço do Opus (conservador)."""
    cost = calculate_cost_brl("modelo-futuro-xyz", tokens_in=1000, tokens_out=500, cambio=5.25)
    cost_opus = calculate_cost_brl("claude-opus-4-6", tokens_in=1000, tokens_out=500, cambio=5.25)
    assert cost == cost_opus
