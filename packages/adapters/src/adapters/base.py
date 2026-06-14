"""ChannelAdapter — contrato único de publicação (doc 01 §3, doc 11 §8.1).

O resto do sistema não conhece APIs específicas de canal.
Credenciais resolvidas via Secret Manager em runtime (nunca em payload).
"""

from typing import Protocol

from pydantic import BaseModel, Field

from core_domain import Canal, Scope


class PublishPayload(BaseModel):
    """Dados necessários para publicar em qualquer canal."""

    scope: Scope
    canal: Canal
    content_id: str
    slot_id: str
    texto: str | None = None
    midias: list[str] = Field(default_factory=list)  # gs:// já renderizados
    meta: dict[str, object] = Field(default_factory=dict)  # primeiro_comentario, titulo_yt, etc.
    idempotency_key: str  # hash(scope, canal, content_id, slot) — doc 01 §3


class PublishResult(BaseModel):
    """Resultado de uma publicação."""

    ok: bool
    post_url: str | None = None
    post_ref: str | None = None  # ID externo do post na plataforma
    erro: str | None = None


class MetricsSnapshot(BaseModel):
    """Snapshot de métricas de um post publicado."""

    post_ref: str
    coletado_em: str  # ISO datetime
    metricas: dict[str, object] = Field(default_factory=dict)


class ValidationIssue(BaseModel):
    """Problema de validação detectado antes da publicação."""

    campo: str
    problema: str


class ChannelAdapter(Protocol):
    """Contrato que todo adapter de canal deve implementar."""

    canal: Canal

    def validate(self, payload: PublishPayload) -> list[ValidationIssue]:
        """Valida payload antes do agendamento (limites de chars, dimensões, etc.)."""
        ...

    async def publish(self, payload: PublishPayload) -> PublishResult:
        """Publica conteúdo no canal. Idempotente (checa publications/ antes)."""
        ...

    async def get_metrics(self, post_ref: str, scope: Scope) -> MetricsSnapshot:
        """Coleta métricas de um post publicado."""
        ...
