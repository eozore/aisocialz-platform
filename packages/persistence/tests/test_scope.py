"""Testes do TenantScope — doc 11 §5.

Verifica que é impossível acessar dados sem escopo.
"""

import pytest

from core_domain.exceptions import ScopeViolationError
from persistence.scope import TenantScope


def test_global_collection_path() -> None:
    scope = TenantScope(tenant_id="victor", brand_id="eozore")
    assert scope.collection_path("marketing_kb") == "platform/marketing_kb"
    assert scope.collection_path("format_catalog") == "platform/format_catalog"


def test_tenant_collection_path() -> None:
    scope = TenantScope(tenant_id="victor")
    assert scope.collection_path("cost_ledger") == "tenant/victor/cost_ledger"
    assert scope.collection_path("team_subscriptions") == "tenant/victor/team_subscriptions"


def test_brand_collection_path() -> None:
    scope = TenantScope(tenant_id="victor", brand_id="eozore")
    assert scope.collection_path("backlog") == "tenant/victor/brands/eozore/backlog"
    assert scope.collection_path("content_graph") == "tenant/victor/brands/eozore/content_graph"


def test_brand_collection_without_brand_raises() -> None:
    """Collection de marca sem brand_id levanta ScopeViolationError."""
    scope = TenantScope(tenant_id="victor")  # sem brand_id
    with pytest.raises(ScopeViolationError, match="exige brand_id"):
        scope.collection_path("backlog")


def test_empty_tenant_id_raises() -> None:
    """tenant_id vazio levanta ScopeViolationError."""
    with pytest.raises(ScopeViolationError, match="tenant_id é obrigatório"):
        TenantScope(tenant_id="")


def test_scope_repr() -> None:
    scope = TenantScope(tenant_id="victor", brand_id="ainewz")
    assert "victor" in repr(scope)
    assert "ainewz" in repr(scope)
