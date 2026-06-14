"""ScopedRepository — acesso genérico ao Firestore com escopo obrigatório (doc 11 §5).

NÃO existe método sem escopo. Query cross-tenant é proibida no código de produto.
"""

from typing import Any, TypeVar

from google.cloud.firestore_v1 import AsyncClient as FirestoreClient
from pydantic import BaseModel

from core_domain.exceptions import ScopeViolationError
from core_domain.models import Scope
from persistence.scope import TenantScope

T = TypeVar("T", bound=BaseModel)


class ScopedRepository:
    """Repositório genérico com escopo de tenant obrigatório.

    Uso:
        scope = TenantScope(tenant_id="victor", brand_id="eozore")
        repo = ScopedRepository(db, scope, BacklogItem, "backlog")
        item = await repo.get("item-123")
    """

    def __init__(
        self,
        db: FirestoreClient,
        scope: TenantScope,
        model: type[T],
        collection: str,
    ) -> None:
        self._db = db
        self._scope = scope
        self._model = model
        self._collection = collection
        self._path = scope.collection_path(collection)

    @property
    def scope(self) -> TenantScope:
        return self._scope

    @property
    def collection_path(self) -> str:
        return self._path

    def _collection_ref(self) -> Any:
        """Retorna a referência à collection no Firestore."""
        # Navega pela hierarquia de subcollections
        parts = self._path.split("/")
        ref: Any = self._db.collection(parts[0])
        for i in range(1, len(parts)):
            ref = ref.document(parts[i]) if i % 2 == 1 else ref.collection(parts[i])
        return ref

    async def get(self, doc_id: str) -> T | None:
        """Busca um documento por ID dentro do escopo."""
        doc_ref = self._collection_ref().document(doc_id)
        doc = await doc_ref.get()
        if not doc.exists:
            return None
        return self._model.model_validate(doc.to_dict())

    async def put(self, entity: T) -> None:
        """Grava um documento. Valida que o escopo do entity bate com o repo."""
        data = entity.model_dump(mode="json")

        # Validação de escopo: se a entidade tem campo 'scope', deve bater
        if hasattr(entity, "scope") and isinstance(entity.scope, Scope):
            entity_scope = entity.scope
            if self._scope.brand_id and entity_scope.brand_id != self._scope.brand_id:
                raise ScopeViolationError(
                    f"Entity brand_id '{entity_scope.brand_id}' "
                    f"!= repo scope brand_id '{self._scope.brand_id}'"
                )
            if entity_scope.tenant_id != self._scope.tenant_id:
                raise ScopeViolationError(
                    f"Entity tenant_id '{entity_scope.tenant_id}' "
                    f"!= repo scope tenant_id '{self._scope.tenant_id}'"
                )

        # Usa o campo 'id' da entidade como document ID
        doc_id = data.get("id", data.get("entry_id"))
        if not doc_id:
            raise ValueError("Entity deve ter campo 'id' para ser persistida")

        doc_ref = self._collection_ref().document(str(doc_id))
        await doc_ref.set(data)

    async def query(self, **filters: Any) -> list[T]:
        """Busca documentos com filtros simples (field == value)."""
        ref = self._collection_ref()
        for field, value in filters.items():
            ref = ref.where(field, "==", value)

        results: list[T] = []
        async for doc in ref.stream():
            results.append(self._model.model_validate(doc.to_dict()))
        return results

    async def delete(self, doc_id: str) -> None:
        """Remove um documento por ID."""
        doc_ref = self._collection_ref().document(doc_id)
        await doc_ref.delete()

    async def increment(self, doc_id: str, field: str, value: float) -> None:
        """Incrementa atomicamente um campo numérico."""
        from google.cloud.firestore_v1 import transforms

        doc_ref = self._collection_ref().document(doc_id)
        await doc_ref.update({field: transforms.Increment(value)})
