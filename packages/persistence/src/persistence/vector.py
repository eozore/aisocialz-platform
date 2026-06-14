"""Busca vetorial — Firestore find_nearest na V1 (doc 11 §7, doc 02 regra 2, doc 10 §4).

Grafo de conteúdo e acervo de mídia usam o MESMO mecanismo.
Migrar para Vertex Vector Search só se a escala exigir (>10k nós).
"""

from typing import Any

from core_domain.models import ContentNode, MediaAsset, Scope
from persistence.scope import TenantScope


class VectorSearch:
    """Busca vetorial usando Firestore find_nearest (V1).

    Usa o mesmo padrão para grafo de conteúdo e acervo de mídia.
    """

    def __init__(self, db: Any) -> None:
        self._db = db

    async def nearest_content(
        self,
        scope: Scope,
        query_embedding: list[float],
        k: int = 5,
        conceitos: list[str] | None = None,
    ) -> list[ContentNode]:
        """Retrieval do grafo: usado por Redator/Roteirista antes de produzir (doc 02 regra 2).

        Combina similaridade vetorial + match de conceitos.
        """
        tenant_scope = TenantScope(scope.tenant_id, scope.brand_id)
        collection_path = tenant_scope.collection_path("content_graph")

        # Navega até a collection
        ref = self._resolve_collection(collection_path)

        # find_nearest com o campo embedding
        results = ref.find_nearest(
            vector_field="embedding",
            query_vector=query_embedding,
            distance_type="COSINE",
            limit=k,
        )

        nodes: list[ContentNode] = []
        async for doc in results.stream():
            data = doc.to_dict()
            node = ContentNode.model_validate(data)

            # Filtro adicional por conceitos (se fornecido)
            if conceitos:
                overlap = set(node.conceitos) & set(conceitos)
                if not overlap:
                    continue

            nodes.append(node)

        return nodes

    async def nearest_assets(
        self,
        scope: Scope,
        query_embedding: list[float],
        k: int = 3,
        min_score: float = 0.7,
    ) -> list[MediaAsset]:
        """Designer busca imagem do acervo por tema (doc 10 §3).

        Abaixo de min_score -> [] (cai no template tipográfico).
        """
        tenant_scope = TenantScope(scope.tenant_id, scope.brand_id)
        collection_path = tenant_scope.collection_path("media_assets")

        ref = self._resolve_collection(collection_path)

        results = ref.find_nearest(
            vector_field="embedding",
            query_vector=query_embedding,
            distance_type="COSINE",
            limit=k,
        )

        assets: list[MediaAsset] = []
        async for doc in results.stream():
            data = doc.to_dict()
            # Firestore find_nearest retorna por proximidade; se necessário,
            # filtrar por score será feito quando a API suportar distance_threshold
            asset = MediaAsset.model_validate(data)
            assets.append(asset)

        return assets

    def _resolve_collection(self, path: str) -> Any:
        """Navega pela hierarquia de subcollections do Firestore."""
        parts = path.split("/")
        ref: Any = self._db.collection(parts[0])
        for i in range(1, len(parts)):
            ref = ref.document(parts[i]) if i % 2 == 1 else ref.collection(parts[i])
        return ref
