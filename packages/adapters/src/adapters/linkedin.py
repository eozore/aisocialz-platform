"""LinkedIn adapter — posts de texto, artigos, imagens e documentos (carrossel PDF).

API: LinkedIn Marketing API (Community Management).
Credenciais via Secret Manager (doc 09 §8).

Formato das credenciais no Secret Manager (JSON):
{
    "access_token": "AQX...",           # OAuth2 Access Token
    "person_urn": "urn:li:person:xxx",  # URN do autor (pessoa)
    "org_urn": "urn:li:organization:xxx"  # Opcional: URN da org (se postar como empresa)
}

Nota: LinkedIn access tokens duram 60 dias; refresh_token dura 365 dias.
O job de saúde de credenciais (doc 08 §5) cuida do refresh.
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

LINKEDIN_API = "https://api.linkedin.com/v2"
LINKEDIN_REST = "https://api.linkedin.com/rest"

# Limites do LinkedIn
LI_TEXT_MAX = 3000  # posts de texto/imagem
LI_ARTICLE_MAX = 120000  # artigos longos
LI_HASHTAG_MAX = 30  # não oficial, mas recomendado


class LinkedInAdapter:
    """Adapter para LinkedIn (posts de texto, imagem, documento/PDF)."""

    canal = Canal.LINKEDIN

    def __init__(self, credential_resolver: CredentialResolver) -> None:
        self._creds = credential_resolver

    def validate(self, payload: PublishPayload) -> list[ValidationIssue]:
        """Valida limites do LinkedIn antes do agendamento."""
        issues: list[ValidationIssue] = []

        formato = str(payload.meta.get("formato", "post_linkedin"))
        max_chars = LI_ARTICLE_MAX if formato == "artigo" else LI_TEXT_MAX

        if payload.texto and len(payload.texto) > max_chars:
            issues.append(
                ValidationIssue(
                    campo="texto",
                    problema=f"Texto excede {max_chars} caracteres ({len(payload.texto)})",
                )
            )

        return issues

    async def publish(self, payload: PublishPayload) -> PublishResult:
        """Publica no LinkedIn via UGC Posts API."""
        try:
            creds = await self._creds.get_credentials(
                payload.scope.tenant_id, payload.scope.brand_id, "linkedin"
            )
        except Exception as e:
            return PublishResult(ok=False, erro=f"Falha ao obter credenciais: {e}")

        token = creds["access_token"]
        # Usa org_urn se disponível, senão person_urn
        author_urn = creds.get("org_urn") or creds.get("person_urn", "")
        formato = str(payload.meta.get("formato", "post_linkedin"))

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                if formato == "carrossel_pdf" and payload.midias:
                    return await self._publish_document(client, token, author_urn, payload)
                elif payload.midias and not formato.startswith("carrossel"):
                    return await self._publish_with_image(client, token, author_urn, payload)
                else:
                    return await self._publish_text(client, token, author_urn, payload)
            except Exception as e:
                return PublishResult(ok=False, erro=str(e))

    async def get_metrics(self, post_ref: str, scope: Scope) -> MetricsSnapshot:
        """Coleta métricas de um post do LinkedIn via organizationalEntityShareStatistics."""
        try:
            creds = await self._creds.get_credentials(scope.tenant_id, scope.brand_id, "linkedin")
        except Exception as e:
            return MetricsSnapshot(
                post_ref=post_ref,
                coletado_em=datetime.now(UTC).isoformat(),
                metricas={"erro": str(e)},
            )

        token = creds["access_token"]

        async with httpx.AsyncClient(timeout=30) as client:
            # Busca estatísticas do share/post
            r = await client.get(
                f"{LINKEDIN_REST}/socialMetadata/{post_ref}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "LinkedIn-Version": "202401",
                    "X-Restli-Protocol-Version": "2.0.0",
                },
            )
            data = r.json()

        return MetricsSnapshot(
            post_ref=post_ref,
            coletado_em=datetime.now(UTC).isoformat(),
            metricas={
                "likes": data.get("reactionSummaries", [{}])[0].get("count", 0)
                if data.get("reactionSummaries")
                else 0,
                "comments": data.get("commentsSummary", {}).get("totalFirstLevelComments", 0),
                "shares": data.get("sharesSummary", {}).get("resharedCount", 0),
            },
        )

    # --- Métodos internos ---

    async def _publish_text(
        self,
        client: httpx.AsyncClient,
        token: str,
        author_urn: str,
        payload: PublishPayload,
    ) -> PublishResult:
        """Post de texto puro."""
        body = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": payload.texto or ""},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }

        r = await client.post(
            f"{LINKEDIN_API}/ugcPosts",
            json=body,
            headers={
                "Authorization": f"Bearer {token}",
                "X-Restli-Protocol-Version": "2.0.0",
            },
        )

        if r.status_code == 201:
            post_id = r.headers.get("x-restli-id", "")
            return PublishResult(
                ok=True,
                post_ref=post_id,
                post_url=f"https://www.linkedin.com/feed/update/{post_id}/",
            )
        return PublishResult(ok=False, erro=f"LinkedIn API {r.status_code}: {r.text}")

    async def _publish_with_image(
        self,
        client: httpx.AsyncClient,
        token: str,
        author_urn: str,
        payload: PublishPayload,
    ) -> PublishResult:
        """Post com imagem (upload via registerUpload + PUT)."""
        # Step 1: Register upload
        reg_body = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": author_urn,
                "serviceRelationships": [
                    {"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}
                ],
            }
        }
        r = await client.post(
            f"{LINKEDIN_API}/assets?action=registerUpload",
            json=reg_body,
            headers={
                "Authorization": f"Bearer {token}",
                "X-Restli-Protocol-Version": "2.0.0",
            },
        )
        if r.status_code != 200:
            return PublishResult(ok=False, erro=f"RegisterUpload falhou: {r.text}")

        reg_data = r.json()["value"]
        upload_url = reg_data["uploadMechanism"][
            "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
        ]["uploadUrl"]
        asset_urn = reg_data["asset"]

        # Step 2: Upload da imagem (assumimos URL pública para GET)
        image_url = payload.midias[0]
        img_r = await client.get(image_url)
        if img_r.status_code != 200:
            return PublishResult(ok=False, erro=f"Falha ao baixar imagem: {image_url}")

        await client.put(
            upload_url,
            content=img_r.content,
            headers={"Authorization": f"Bearer {token}"},
        )

        # Step 3: Criar post com a imagem
        body = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": payload.texto or ""},
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {
                            "status": "READY",
                            "media": asset_urn,
                        }
                    ],
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }

        r = await client.post(
            f"{LINKEDIN_API}/ugcPosts",
            json=body,
            headers={
                "Authorization": f"Bearer {token}",
                "X-Restli-Protocol-Version": "2.0.0",
            },
        )

        if r.status_code == 201:
            post_id = r.headers.get("x-restli-id", "")
            return PublishResult(ok=True, post_ref=post_id)
        return PublishResult(ok=False, erro=f"LinkedIn post+image {r.status_code}: {r.text}")

    async def _publish_document(
        self,
        client: httpx.AsyncClient,
        token: str,
        author_urn: str,
        payload: PublishPayload,
    ) -> PublishResult:
        """Post com documento (carrossel PDF). Usa a Documents API."""
        # Step 1: Register upload para documento
        reg_body = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-document"],
                "owner": author_urn,
                "serviceRelationships": [
                    {"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}
                ],
            }
        }
        r = await client.post(
            f"{LINKEDIN_API}/assets?action=registerUpload",
            json=reg_body,
            headers={
                "Authorization": f"Bearer {token}",
                "X-Restli-Protocol-Version": "2.0.0",
            },
        )
        if r.status_code != 200:
            return PublishResult(ok=False, erro=f"RegisterUpload doc falhou: {r.text}")

        reg_data = r.json()["value"]
        upload_url = reg_data["uploadMechanism"][
            "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
        ]["uploadUrl"]
        asset_urn = reg_data["asset"]

        # Step 2: Upload do PDF
        doc_url = payload.midias[0]
        doc_r = await client.get(doc_url)
        if doc_r.status_code != 200:
            return PublishResult(ok=False, erro=f"Falha ao baixar documento: {doc_url}")

        await client.put(
            upload_url,
            content=doc_r.content,
            headers={"Authorization": f"Bearer {token}"},
        )

        # Step 3: Criar post com documento
        title = str(payload.meta.get("titulo_documento", "Documento"))
        body = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": payload.texto or ""},
                    "shareMediaCategory": "NATIVE_DOCUMENT",
                    "media": [
                        {
                            "status": "READY",
                            "media": asset_urn,
                            "title": {"text": title},
                        }
                    ],
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }

        r = await client.post(
            f"{LINKEDIN_API}/ugcPosts",
            json=body,
            headers={
                "Authorization": f"Bearer {token}",
                "X-Restli-Protocol-Version": "2.0.0",
            },
        )

        if r.status_code == 201:
            post_id = r.headers.get("x-restli-id", "")
            return PublishResult(ok=True, post_ref=post_id)
        return PublishResult(ok=False, erro=f"LinkedIn doc post {r.status_code}: {r.text}")
