"""Blog adapter — publicação via API HTTP do site próprio (éozoré) ou commit.

Formato das credenciais no Secret Manager (JSON):
{
    "api_url": "https://eozore.com/api/posts",  # endpoint de criação de post
    "api_key": "sk-...",                          # chave de autenticação
    "method": "api"                               # "api" ou "git" (futuro)
}

Para AINewz, o blog/portal é gerido pelo projeto separado — este adapter
só publica formatos novos que a plataforma gera (doc 06 §5.5).
"""

from datetime import UTC, datetime

import httpx

from adapters.base import (
    MetricsSnapshot,
    PublishPayload,
    PublishResult,
    ValidationIssue,
)
from adapters.credentials import CredentialResolver
from core_domain import Canal, Scope

BLOG_TITLE_MAX = 200
BLOG_BODY_MIN = 100  # mínimo razoável para um post de blog


class BlogAdapter:
    """Adapter para blog (via API HTTP do site próprio)."""

    canal = Canal.BLOG

    def __init__(self, credential_resolver: CredentialResolver) -> None:
        self._creds = credential_resolver

    def validate(self, payload: PublishPayload) -> list[ValidationIssue]:
        """Validações básicas para blog posts."""
        issues: list[ValidationIssue] = []

        titulo = str(payload.meta.get("titulo", ""))
        if titulo and len(titulo) > BLOG_TITLE_MAX:
            issues.append(
                ValidationIssue(
                    campo="meta.titulo",
                    problema=f"Título excede {BLOG_TITLE_MAX} caracteres",
                )
            )

        if payload.texto and len(payload.texto) < BLOG_BODY_MIN:
            issues.append(
                ValidationIssue(
                    campo="texto",
                    problema=f"Corpo do blog muito curto (mín {BLOG_BODY_MIN} chars)",
                )
            )

        return issues

    async def publish(self, payload: PublishPayload) -> PublishResult:
        """Publica no blog via API HTTP."""
        try:
            creds = await self._creds.get_credentials(
                payload.scope.tenant_id, payload.scope.brand_id, "blog"
            )
        except Exception as e:
            return PublishResult(ok=False, erro=f"Falha ao obter credenciais: {e}")

        api_url = creds.get("api_url", "")
        api_key = creds.get("api_key", "")

        if not api_url:
            return PublishResult(ok=False, erro="api_url não configurada nas credenciais do blog")

        body = {
            "title": str(payload.meta.get("titulo", "Sem título")),
            "content": payload.texto or "",
            "slug": str(payload.meta.get("slug", payload.content_id)),
            "status": "published",
            "tags": payload.meta.get("tags", []),
            "featured_image": payload.midias[0] if payload.midias else None,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                api_url,
                json=body,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
            )

            if r.status_code in (200, 201):
                data = r.json()
                post_url = data.get("url") or data.get("permalink") or ""
                post_id = data.get("id") or data.get("slug") or payload.content_id
                return PublishResult(ok=True, post_ref=str(post_id), post_url=post_url)

            return PublishResult(ok=False, erro=f"Blog API {r.status_code}: {r.text[:200]}")

    async def get_metrics(self, post_ref: str, scope: Scope) -> MetricsSnapshot:
        """Métricas do blog vêm do Google Analytics (implementado pelo Analista).

        O adapter retorna placeholder; métricas reais via GA Integration.
        """
        return MetricsSnapshot(
            post_ref=post_ref,
            coletado_em=datetime.now(UTC).isoformat(),
            metricas={"nota": "Métricas de blog via Google Analytics (Analista)"},
        )
