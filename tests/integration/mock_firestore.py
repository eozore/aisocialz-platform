"""Mock in-memory do Firestore AsyncClient para testes de integração.

Simula a API real (collection/document/get/set/update/stream) sem
necessidade de emulador Java ou conexão GCP.
"""

from typing import Any


class MockDocument:
    """Simula um DocumentSnapshot."""

    def __init__(self, data: dict | None = None):
        self._data = data

    @property
    def exists(self) -> bool:
        return self._data is not None

    def to_dict(self) -> dict:
        return self._data or {}


class MockDocumentRef:
    """Simula uma DocumentReference."""

    def __init__(self, store: dict, path: str):
        self._store = store
        self._path = path

    async def get(self) -> MockDocument:
        data = self._store.get(self._path)
        return MockDocument(data)

    async def set(self, data: dict, merge: bool = False) -> None:
        if merge and self._path in self._store:
            existing = self._store[self._path]
            existing.update(data)
        else:
            self._store[self._path] = dict(data)

    async def update(self, data: dict) -> None:
        if self._path in self._store:
            self._store[self._path].update(data)
        else:
            self._store[self._path] = dict(data)

    async def delete(self) -> None:
        self._store.pop(self._path, None)

    def collection(self, name: str) -> "MockCollectionRef":
        return MockCollectionRef(self._store, f"{self._path}/{name}")


class MockCollectionRef:
    """Simula uma CollectionReference."""

    def __init__(self, store: dict, path: str):
        self._store = store
        self._path = path

    def document(self, doc_id: str) -> MockDocumentRef:
        return MockDocumentRef(self._store, f"{self._path}/{doc_id}")

    async def stream(self):
        """Itera documentos na collection."""
        prefix = self._path + "/"
        for key, value in list(self._store.items()):
            # Só documentos diretos desta collection (sem subcollections)
            if key.startswith(prefix):
                remaining = key[len(prefix) :]
                if "/" not in remaining:
                    yield MockDocument(value)

    def where(self, field: str, op: str, value: Any) -> "MockCollectionRef":
        """Filtro simplificado (retorna self para encadear)."""
        # TODO: implementar filtro real se necessário
        return self


class MockCollectionGroup:
    """Simula collection_group (busca em todas as subcollections com mesmo nome)."""

    def __init__(self, store: dict, collection_name: str):
        self._store = store
        self._name = collection_name

    async def stream(self):
        """Itera todos os documentos em qualquer subcollection com este nome."""
        for key, value in list(self._store.items()):
            parts = key.split("/")
            # Procura o nome da collection no path
            for i, part in enumerate(parts):
                if part == self._name and i < len(parts) - 1:
                    yield MockDocument(value)
                    break


class MockFirestoreClient:
    """Mock completo do AsyncClient do Firestore."""

    def __init__(self):
        self._store: dict[str, dict] = {}

    def collection(self, name: str) -> MockCollectionRef:
        return MockCollectionRef(self._store, name)

    def document(self, path: str) -> MockDocumentRef:
        return MockDocumentRef(self._store, path)

    def collection_group(self, name: str) -> MockCollectionGroup:
        return MockCollectionGroup(self._store, name)

    @property
    def data(self) -> dict:
        """Acesso direto ao store para debug."""
        return self._store
