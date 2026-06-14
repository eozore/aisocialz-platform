"""Testes dos tipos de domínio."""

from core_domain import (
    BacklogItem,
    BudgetExceededError,
    CostEntry,
    Funil,
    ItemStatus,
    PlatformPausedError,
    Recommendation,
    Scope,
    TenantConfig,
)


def test_scope_creation() -> None:
    scope = Scope(tenant_id="victor", brand_id="eozore")
    assert scope.tenant_id == "victor"
    assert scope.brand_id == "eozore"


def test_backlog_item_defaults() -> None:
    item = BacklogItem(
        id="item-1",
        scope=Scope(tenant_id="victor", brand_id="eozore"),
        tipo="carrossel",
        pilar="fundamentos sem medo",
        funil=Funil.TOPO,
        fonte={"tipo": "pauta", "ref": None},
    )
    assert item.status == ItemStatus.IDEIA
    assert item.requer_ceo is False
    assert item.referencias_grafo == []


def test_recommendation_valid() -> None:
    rec = Recommendation(
        posicao="Priorizar carrosséis",
        evidencia=["learning-001"],
        contra_argumento="Reels têm maior alcance orgânico",
        confianca=0.7,
        o_que_mudaria_confianca="3 semanas de dados comparativos",
    )
    assert rec.is_valid()


def test_recommendation_invalid_empty_posicao() -> None:
    rec = Recommendation(
        posicao="",
        evidencia=[],
        contra_argumento="algo",
        confianca=0.5,
        o_que_mudaria_confianca="algo",
    )
    assert not rec.is_valid()


def test_cost_entry_creation() -> None:
    entry = CostEntry(
        id="cost-1",
        scope=Scope(tenant_id="victor", brand_id="eozore"),
        agente="redator",
        servico="vertex_llm",
        modelo="claude-opus-4-6",
        tokens_in=1000,
        tokens_out=500,
        custo_estimado_brl=0.42,
    )
    assert entry.conta.value == "operacao"
    assert entry.custo_estimado_brl == 0.42


def test_tenant_config_defaults() -> None:
    config = TenantConfig(tenant_id="victor")
    assert config.platform_status.value == "ativo"
    assert config.budget_mensal_brl == 600.0
    assert config.gasto_mes_ledger_brl == 0.0


def test_platform_paused_error() -> None:
    err = PlatformPausedError("teste")
    assert str(err) == "teste"


def test_budget_exceeded_error() -> None:
    err = BudgetExceededError("over", custo_brl=3.5)
    assert err.custo_brl == 3.5
