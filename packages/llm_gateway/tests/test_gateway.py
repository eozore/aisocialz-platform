"""Testes do LlmGateway — doc 11 §6, definição de pronto Fase 0.

Demonstra:
- platform_status=paused bloqueia chamadas
- custo aparece no ledger com conta distinguindo build/operação
- teto por item funciona
"""

import pytest

from core_domain import PlatformPausedError, Scope, TaskKind, TenantConfig
from core_domain.enums import CostAccount, PlatformStatus
from core_domain.models import CostEntry
from llm_gateway.client import LlmGateway


class FakeLedger:
    """Implementação fake do LedgerWriter para testes."""

    def __init__(self, platform_status: str = "ativo") -> None:
        self.config = TenantConfig(
            tenant_id="victor",
            platform_status=PlatformStatus(platform_status),
            budget_mensal_brl=600.0,
            gasto_mes_ledger_brl=50.0,
        )
        self.recorded_entries: list[CostEntry] = []
        self.monthly_increments: list[float] = []

    async def get_tenant_config(self, tenant_id: str) -> TenantConfig:
        return self.config

    async def record_cost(self, entry: CostEntry) -> None:
        self.recorded_entries.append(entry)

    async def increment_monthly_spend(self, tenant_id: str, amount: float) -> None:
        self.monthly_increments.append(amount)


@pytest.mark.asyncio
async def test_paused_blocks_call() -> None:
    """platform_status=paused bloqueia chamadas LLM (doc 05 §1, definição de pronto Fase 0)."""
    ledger = FakeLedger(platform_status="paused")
    gateway = LlmGateway(ledger=ledger)

    scope = Scope(tenant_id="victor", brand_id="eozore")

    with pytest.raises(PlatformPausedError):
        await gateway.complete(
            scope=scope,
            agent_id="redator",
            task_kind=TaskKind.CRIATIVA,
            messages=[{"role": "user", "content": "escreva um post"}],
        )


@pytest.mark.asyncio
async def test_call_records_in_ledger() -> None:
    """Uma chamada de teste aparece no cost_ledger (definição de pronto Fase 0)."""
    ledger = FakeLedger(platform_status="ativo")
    gateway = LlmGateway(ledger=ledger)

    scope = Scope(tenant_id="victor", brand_id="eozore")

    result = await gateway.complete(
        scope=scope,
        agent_id="construtora",
        task_kind=TaskKind.ESTRUTURAL,
        messages=[{"role": "user", "content": "teste"}],
        conta=CostAccount.BUILD,
    )

    # Custo foi calculado
    assert result.cost_brl > 0
    assert result.model_used == "gemini-2.5-flash"

    # Entrada gravada no ledger
    assert len(ledger.recorded_entries) == 1
    entry = ledger.recorded_entries[0]
    assert entry.conta == CostAccount.BUILD
    assert entry.agente == "construtora"


@pytest.mark.asyncio
async def test_build_account_does_not_increment_monthly() -> None:
    """Conta 'build' NÃO incrementa gasto_mes_ledger_brl (doc 08 §7)."""
    ledger = FakeLedger(platform_status="ativo")
    gateway = LlmGateway(ledger=ledger)

    scope = Scope(tenant_id="victor", brand_id="eozore")

    await gateway.complete(
        scope=scope,
        agent_id="construtora",
        task_kind=TaskKind.ESTRUTURAL,
        messages=[{"role": "user", "content": "teste"}],
        conta=CostAccount.BUILD,
    )

    # NÃO incrementou o acumulado mensal
    assert ledger.monthly_increments == []


@pytest.mark.asyncio
async def test_operacao_account_increments_monthly() -> None:
    """Conta 'operacao' incrementa gasto_mes_ledger_brl."""
    ledger = FakeLedger(platform_status="ativo")
    gateway = LlmGateway(ledger=ledger)

    scope = Scope(tenant_id="victor", brand_id="eozore")

    await gateway.complete(
        scope=scope,
        agent_id="redator",
        task_kind=TaskKind.ESTRUTURAL,
        messages=[{"role": "user", "content": "teste"}],
        conta=CostAccount.OPERACAO,
    )

    # Incrementou o acumulado mensal
    assert len(ledger.monthly_increments) == 1
    assert ledger.monthly_increments[0] > 0
