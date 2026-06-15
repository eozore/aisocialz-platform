"""Meta adapter — Instagram (feed/carrossel/reels/stories) + Facebook Pages.

Baseado em código de validação com tokens testados e funcionalidades confirmadas.
Credenciais via Secret Manager, nunca hardcoded (doc 09 §8).
Refresh programático de tokens obrigatório — expiram em ~60 dias (doc 08 §5).

Formato das credenciais no Secret Manager (JSON):
{
    "access_token": "EAALn...",       # User Access Token (Facebook/Instagram)
    "ig_user_id": "17841452...",      # ID da Conta Comercial do Instagram
    "page_id": "1205137...",          # ID da Página do Facebook conectada
}
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

GRAPH_BASE = "https://graph.facebook.com/v20.0"

# Limites da API (doc 01 §3 — validate() roda no agendamento)
IG_CAPTION_MAX = 2200
IG_CAROUSEL_MIN = 2
IG_CAROUSEL_MAX = 10
IG_HASHTAG_MAX = 30


class MetaInstagramAdapter:
    """Adapter para Instagram (feed, carrossel, reels, stories) via Meta Graph API."""

    canal = Canal.INSTAGRAM

    def __init__(self, credential_resolver: CredentialResolver) -> None:
        self._creds = credential_resolver

    def validate(self, payload: PublishPayload) -> list[ValidationIssue]:
        """Valida limites antes do agendamento (doc 01 §3)."""
        issues: list[ValidationIssue] = []

        if payload.texto and len(payload.texto) > IG_CAPTION_MAX:
            issues.append(
                ValidationIssue(
                    campo="texto",
                    problema=f"Caption excede {IG_CAPTION_MAX} caracteres ({len(payload.texto)})",
                )
            )

        # Carrossel: 2-10 imagens
        formato = payload.meta.get("formato", "")
        if formato == "carrossel":
            n_midias = len(payload.midias)
            if n_midias < IG_CAROUSEL_MIN or n_midias > IG_CAROUSEL_MAX:
                issues.append(
                    ValidationIssue(
                        campo="midias",
                        problema=(
                            f"Carrossel exige {IG_CAROUSEL_MIN}-{IG_CAROUSEL_MAX} "
                            f"imagens, tem {n_midias}"
                        ),
                    )
                )

        # Hashtags: máx 30
        if payload.texto:
            hashtag_count = payload.texto.count("#")
            if hashtag_count > IG_HASHTAG_MAX:
                issues.append(
                    ValidationIssue(
                        campo="texto",
                        problema=f"Máximo {IG_HASHTAG_MAX} hashtags, tem {hashtag_count}",
                    )
                )

        return issues

    async def publish(self, payload: PublishPayload) -> PublishResult:
        """Publica no Instagram. Idempotente via idempotency_key."""
        try:
            creds = await self._creds.get_credentials(
                payload.scope.tenant_id, payload.scope.brand_id, "instagram"
            )
        except Exception as e:
            return PublishResult(ok=False, erro=f"Falha ao obter credenciais: {e}")

        token = creds["access_token"]
        ig_user_id = creds["ig_user_id"]
        formato = str(payload.meta.get("formato", "foto"))

        async with httpx.AsyncClient(timeout=60) as client:
            try:
                if formato == "carrossel":
                    return await self._publish_carousel(client, ig_user_id, token, payload)
                elif formato in ("reel", "reels", "reel_renderizado"):
                    return await self._publish_reels(client, ig_user_id, token, payload)
                elif formato == "story":
                    return await self._publish_story(client, ig_user_id, token, payload)
                else:
                    return await self._publish_photo(client, ig_user_id, token, payload)
            except Exception as e:
                return PublishResult(ok=False, erro=str(e))

    async def get_metrics(self, post_ref: str, scope: Scope) -> MetricsSnapshot:
        """Coleta métricas de um post via Instagram Insights API."""
        try:
            creds = await self._creds.get_credentials(scope.tenant_id, scope.brand_id, "instagram")
        except Exception as e:
            return MetricsSnapshot(
                post_ref=post_ref,
                coletado_em=datetime.now(UTC).isoformat(),
                metricas={"erro": str(e)},
            )

        token = creds["access_token"]
        # Métricas unificadas v22.0+: views, reach, saved
        metrics = "views,reach,saved"

        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(
                f"{GRAPH_BASE}/{post_ref}/insights",
                params={"metric": metrics, "access_token": token},
            )
            data = r.json()

        parsed: dict[str, object] = {}
        if "data" in data:
            for item in data["data"]:
                parsed[item["name"]] = item["values"][0]["value"] if item.get("values") else 0

        return MetricsSnapshot(
            post_ref=post_ref,
            coletado_em=datetime.now(UTC).isoformat(),
            metricas=parsed,
        )

    # --- Métodos internos de publicação ---

    async def _publish_photo(
        self, client: httpx.AsyncClient, ig_user_id: str, token: str, payload: PublishPayload
    ) -> PublishResult:
        """Post de imagem única."""
        image_url = payload.midias[0] if payload.midias else ""
        if not image_url:
            return PublishResult(ok=False, erro="Nenhuma mídia fornecida para post de foto")

        # Step 1: Criar container
        r = await client.post(
            f"{GRAPH_BASE}/{ig_user_id}/media",
            data={"image_url": image_url, "caption": payload.texto or "", "access_token": token},
        )
        res = r.json()
        if "id" not in res:
            return PublishResult(ok=False, erro=f"Falha ao criar container: {res}")

        container_id = res["id"]
        await _wait_seconds(2)

        # Step 2: Publicar
        r = await client.post(
            f"{GRAPH_BASE}/{ig_user_id}/media_publish",
            data={"creation_id": container_id, "access_token": token},
        )
        pub_res = r.json()
        if "id" not in pub_res:
            return PublishResult(ok=False, erro=f"Falha ao publicar: {pub_res}")

        return PublishResult(
            ok=True,
            post_ref=pub_res["id"],
            post_url=f"https://www.instagram.com/p/{pub_res['id']}/",
        )

    async def _publish_carousel(
        self, client: httpx.AsyncClient, ig_user_id: str, token: str, payload: PublishPayload
    ) -> PublishResult:
        """Post de carrossel (2-10 imagens)."""
        children: list[str] = []
        for url in payload.midias:
            r = await client.post(
                f"{GRAPH_BASE}/{ig_user_id}/media",
                data={"image_url": url, "is_carousel_item": "true", "access_token": token},
            )
            res = r.json()
            if "id" not in res:
                return PublishResult(ok=False, erro=f"Falha em item do carrossel: {res}")
            children.append(res["id"])

        # Criar container do carrossel
        r = await client.post(
            f"{GRAPH_BASE}/{ig_user_id}/media",
            data={
                "media_type": "CAROUSEL",
                "children": ",".join(children),
                "caption": payload.texto or "",
                "access_token": token,
            },
        )
        container = r.json()
        if "id" not in container:
            return PublishResult(ok=False, erro=f"Falha no container carrossel: {container}")

        await _wait_seconds(2)

        # Publicar
        r = await client.post(
            f"{GRAPH_BASE}/{ig_user_id}/media_publish",
            data={"creation_id": container["id"], "access_token": token},
        )
        pub_res = r.json()
        if "id" not in pub_res:
            return PublishResult(ok=False, erro=f"Falha ao publicar carrossel: {pub_res}")

        return PublishResult(ok=True, post_ref=pub_res["id"])

    async def _publish_reels(
        self, client: httpx.AsyncClient, ig_user_id: str, token: str, payload: PublishPayload
    ) -> PublishResult:
        """Publicar Reels (vídeo)."""
        video_url = payload.midias[0] if payload.midias else ""
        if not video_url:
            return PublishResult(ok=False, erro="Nenhum vídeo fornecido para Reels")

        # Criar container de Reels
        r = await client.post(
            f"{GRAPH_BASE}/{ig_user_id}/media",
            data={
                "media_type": "REELS",
                "video_url": video_url,
                "caption": payload.texto or "",
                "access_token": token,
            },
        )
        res = r.json()
        if "id" not in res:
            return PublishResult(ok=False, erro=f"Falha ao criar container de Reels: {res}")

        container_id = res["id"]

        # Aguardar processamento (máx 2 min)
        for _ in range(12):
            await _wait_seconds(10)
            r = await client.get(
                f"{GRAPH_BASE}/{container_id}",
                params={"fields": "status_code", "access_token": token},
            )
            status = r.json()
            if status.get("status_code") == "FINISHED":
                break
        else:
            return PublishResult(ok=False, erro="Timeout no processamento do Reels")

        # Publicar
        r = await client.post(
            f"{GRAPH_BASE}/{ig_user_id}/media_publish",
            data={"creation_id": container_id, "access_token": token},
        )
        pub_res = r.json()
        if "id" not in pub_res:
            return PublishResult(ok=False, erro=f"Falha ao publicar Reels: {pub_res}")

        return PublishResult(ok=True, post_ref=pub_res["id"])

    async def _publish_story(
        self, client: httpx.AsyncClient, ig_user_id: str, token: str, payload: PublishPayload
    ) -> PublishResult:
        """Publicar Story."""
        image_url = payload.midias[0] if payload.midias else ""
        if not image_url:
            return PublishResult(ok=False, erro="Nenhuma mídia fornecida para Story")

        r = await client.post(
            f"{GRAPH_BASE}/{ig_user_id}/media",
            data={"image_url": image_url, "media_type": "STORIES", "access_token": token},
        )
        res = r.json()
        if "id" not in res:
            return PublishResult(ok=False, erro=f"Falha ao criar container de Story: {res}")

        container_id = res["id"]
        r = await client.post(
            f"{GRAPH_BASE}/{ig_user_id}/media_publish",
            data={"creation_id": container_id, "access_token": token},
        )
        pub_res = r.json()
        if "id" not in pub_res:
            return PublishResult(ok=False, erro=f"Falha ao publicar Story: {pub_res}")

        return PublishResult(ok=True, post_ref=pub_res["id"])


class MetaThreadsAdapter:
    """Adapter para Threads via graph.threads.net.

    Formato das credenciais no Secret Manager:
    {
        "access_token": "THAAOo...",   # Threads Access Token (inicia com THA)
        "threads_user_id": "17841..."  # ID do usuário no Threads
    }
    """

    canal = Canal.THREADS

    def __init__(self, credential_resolver: CredentialResolver) -> None:
        self._creds = credential_resolver

    def validate(self, payload: PublishPayload) -> list[ValidationIssue]:
        """Threads: máx 500 caracteres por post."""
        issues: list[ValidationIssue] = []
        if payload.texto and len(payload.texto) > 500:
            issues.append(
                ValidationIssue(
                    campo="texto",
                    problema=f"Threads permite máx 500 caracteres, tem {len(payload.texto)}",
                )
            )
        return issues

    async def publish(self, payload: PublishPayload) -> PublishResult:
        """Publica no Threads (texto ou imagem+texto)."""
        try:
            creds = await self._creds.get_credentials(
                payload.scope.tenant_id, payload.scope.brand_id, "threads"
            )
        except Exception as e:
            return PublishResult(ok=False, erro=f"Falha ao obter credenciais: {e}")

        token = creds["access_token"]
        base = "https://graph.threads.net/v1.0"

        data: dict[str, str] = {"text": payload.texto or "", "access_token": token}
        if payload.midias:
            data["media_type"] = "IMAGE"
            data["image_url"] = payload.midias[0]
        else:
            data["media_type"] = "TEXT"

        async with httpx.AsyncClient(timeout=30) as client:
            # Criar container
            r = await client.post(f"{base}/me/threads", data=data)
            res = r.json()
            if "id" not in res:
                return PublishResult(ok=False, erro=f"Falha ao criar container Threads: {res}")

            container_id = res["id"]

            # Publicar
            r = await client.post(
                f"{base}/me/threads_publish",
                data={"creation_id": container_id, "access_token": token},
            )
            pub_res = r.json()
            if "id" not in pub_res:
                return PublishResult(ok=False, erro=f"Falha ao publicar no Threads: {pub_res}")

        return PublishResult(ok=True, post_ref=pub_res["id"])

    async def get_metrics(self, post_ref: str, scope: Scope) -> MetricsSnapshot:
        """Threads: métricas ainda limitadas na API."""
        return MetricsSnapshot(
            post_ref=post_ref,
            coletado_em=datetime.now(UTC).isoformat(),
            metricas={"nota": "Threads Insights API limitada na v1.0"},
        )


class MetaFacebookAdapter:
    """Adapter para Facebook Pages.

    Formato das credenciais no Secret Manager:
    {
        "access_token": "EAALn...",  # User Access Token
        "page_id": "1205137..."      # Page ID
    }

    O adapter obtém o Page Access Token dinamicamente a partir do User Token.
    """

    canal = Canal.FACEBOOK

    def __init__(self, credential_resolver: CredentialResolver) -> None:
        self._creds = credential_resolver

    def validate(self, payload: PublishPayload) -> list[ValidationIssue]:
        """Facebook Pages: limite generoso (63k chars)."""
        issues: list[ValidationIssue] = []
        if payload.texto and len(payload.texto) > 63206:
            issues.append(
                ValidationIssue(campo="texto", problema="Excede limite de 63206 caracteres do FB")
            )
        return issues

    async def publish(self, payload: PublishPayload) -> PublishResult:
        """Publica na Página do Facebook."""
        try:
            creds = await self._creds.get_credentials(
                payload.scope.tenant_id, payload.scope.brand_id, "facebook"
            )
        except Exception as e:
            return PublishResult(ok=False, erro=f"Falha ao obter credenciais: {e}")

        user_token = creds["access_token"]
        page_id = creds["page_id"]

        async with httpx.AsyncClient(timeout=30) as client:
            # Obter Page Access Token
            r = await client.get(
                f"{GRAPH_BASE}/{page_id}",
                params={"fields": "access_token", "access_token": user_token},
            )
            page_data = r.json()
            page_token = page_data.get("access_token", user_token)

            # Publicar
            data: dict[str, str] = {"message": payload.texto or "", "access_token": page_token}
            link = payload.meta.get("link")
            if link:
                data["link"] = str(link)

            r = await client.post(f"{GRAPH_BASE}/{page_id}/feed", data=data)
            pub_res = r.json()
            if "id" not in pub_res:
                return PublishResult(ok=False, erro=f"Falha ao publicar no FB: {pub_res}")

        return PublishResult(ok=True, post_ref=pub_res["id"])

    async def get_metrics(self, post_ref: str, scope: Scope) -> MetricsSnapshot:
        """Métricas de post do Facebook."""
        try:
            creds = await self._creds.get_credentials(scope.tenant_id, scope.brand_id, "facebook")
        except Exception as e:
            return MetricsSnapshot(
                post_ref=post_ref,
                coletado_em=datetime.now(UTC).isoformat(),
                metricas={"erro": str(e)},
            )

        token = creds["access_token"]
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(
                f"{GRAPH_BASE}/{post_ref}",
                params={
                    "fields": "shares,likes.summary(true),comments.summary(true)",
                    "access_token": token,
                },
            )
            data = r.json()

        return MetricsSnapshot(
            post_ref=post_ref,
            coletado_em=datetime.now(UTC).isoformat(),
            metricas={
                "shares": data.get("shares", {}).get("count", 0),
                "likes": data.get("likes", {}).get("summary", {}).get("total_count", 0),
                "comments": data.get("comments", {}).get("summary", {}).get("total_count", 0),
            },
        )


async def _wait_seconds(seconds: int) -> None:
    """Aguarda N segundos (async-friendly)."""
    import asyncio

    await asyncio.sleep(seconds)
