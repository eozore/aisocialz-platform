"""Testes de routing de modelos — doc 03 §1, doc 11 §6."""

from core_domain.enums import PlatformStatus, TaskKind
from llm_gateway.routing import resolve_model


def test_routing_normal_criativa() -> None:
    model = resolve_model(TaskKind.CRIATIVA, PlatformStatus.ATIVO)
    assert model == "claude-opus-4-6"


def test_routing_normal_estrutural() -> None:
    model = resolve_model(TaskKind.ESTRUTURAL, PlatformStatus.ATIVO)
    assert model == "gemini-2.5-flash"


def test_routing_economia_rebaixa_criativa() -> None:
    """Em modo economia, criativa rebaixa de Opus para Sonnet (doc 05 §1)."""
    model = resolve_model(TaskKind.CRIATIVA, PlatformStatus.ECONOMIA)
    assert model == "claude-sonnet-4-6"


def test_routing_economia_rebaixa_analitica() -> None:
    """Em modo economia, analítica rebaixa de Pro para Flash."""
    model = resolve_model(TaskKind.ANALITICA, PlatformStatus.ECONOMIA)
    assert model == "gemini-2.5-flash"


def test_routing_embedding_always_cheap() -> None:
    """Embedding usa sempre o mais barato, independente do modo."""
    assert resolve_model(TaskKind.EMBEDDING, PlatformStatus.ATIVO) == "text-embedding-005"
    assert resolve_model(TaskKind.EMBEDDING, PlatformStatus.ECONOMIA) == "text-embedding-005"
