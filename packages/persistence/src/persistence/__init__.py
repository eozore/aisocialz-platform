"""persistence — acesso a Firestore com escopo de tenant obrigatório."""

from persistence.repository import ScopedRepository
from persistence.scope import GLOBAL_COLLECTIONS, TENANT_COLLECTIONS, TenantScope
from persistence.vector import VectorSearch

__all__ = [
    "GLOBAL_COLLECTIONS",
    "ScopedRepository",
    "TENANT_COLLECTIONS",
    "TenantScope",
    "VectorSearch",
]
