"""TenantScope — resolve caminhos Firestore com escopo obrigatório (doc 11 §5).

Toda operação de dados passa por aqui. É impossível acessar sem escopo.
"""

from core_domain.exceptions import ScopeViolationError

# Collections globais vivem sob platform/ (doc 02)
GLOBAL_COLLECTIONS = frozenset(
    {
        "marketing_kb",
        "format_catalog",
        "pricing",
        "model_routing",
    }
)

# Collections de tenant (não exigem brand_id)
TENANT_COLLECTIONS = frozenset(
    {
        "cost_ledger",
        "team_subscriptions",
        "config",
        "approvals",
        "brands",
    }
)


class TenantScope:
    """Resolve o caminho Firestore. Toda operação passa por aqui.

    Garante que:
    - Collections globais apontam para platform/{name}
    - Collections de tenant apontam para tenant/{tenant_id}/{name}
    - Collections de marca apontam para tenant/{tenant_id}/brands/{brand_id}/{name}
    """

    def __init__(self, tenant_id: str, brand_id: str | None = None) -> None:
        if not tenant_id:
            raise ScopeViolationError("tenant_id é obrigatório")
        self.tenant_id = tenant_id
        self.brand_id = brand_id

    def collection_path(self, name: str) -> str:
        """Resolve o caminho completo da collection no Firestore."""
        if name in GLOBAL_COLLECTIONS:
            return f"platform/{name}"
        if name in TENANT_COLLECTIONS:
            return f"tenant/{self.tenant_id}/{name}"
        # Collection por marca — exige brand_id
        if not self.brand_id:
            raise ScopeViolationError(
                f"Collection '{name}' exige brand_id, mas o escopo não tem brand definido"
            )
        return f"tenant/{self.tenant_id}/brands/{self.brand_id}/{name}"

    def __repr__(self) -> str:
        return f"TenantScope(tenant_id={self.tenant_id!r}, brand_id={self.brand_id!r})"
