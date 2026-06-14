"""Testes do AdapterRegistry — doc 09 §3.

Verifica que times inativos não entregam adapter.
"""

import pytest

from adapters.credentials import CredentialResolver
from adapters.registry import AdapterRegistry
from core_domain import Canal, TeamInactiveError


def test_active_team_returns_adapter() -> None:
    registry = AdapterRegistry(
        credential_resolver=CredentialResolver(),
        active_teams={"meta", "linkedin", "blog"},
    )
    adapter = registry.get_adapter(Canal.INSTAGRAM)
    assert adapter.canal == Canal.INSTAGRAM


def test_inactive_team_raises() -> None:
    registry = AdapterRegistry(
        credential_resolver=CredentialResolver(),
        active_teams={"linkedin"},  # meta não está ativo
    )
    with pytest.raises(TeamInactiveError, match="meta"):
        registry.get_adapter(Canal.INSTAGRAM)


def test_available_canals_only_active() -> None:
    registry = AdapterRegistry(
        credential_resolver=CredentialResolver(),
        active_teams={"meta"},  # só meta ativo
    )
    canals = registry.available_canals()
    assert Canal.INSTAGRAM in canals
    assert Canal.THREADS in canals
    assert Canal.FACEBOOK in canals
