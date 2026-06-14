"""Resolução de credenciais via Secret Manager — doc 09 §8.

Caminho escopado: {tenant_id}--{brand_id}--{canal}--credentials
Só svc-publisher acessa em runtime (doc 01 §4).
Nenhum agente, nenhum prompt, nunca o cockpit recebe segredos.
"""

import json
from typing import Any


class CredentialResolver:
    """Resolve credenciais de canal a partir do Secret Manager."""

    def __init__(self, secret_client: Any | None = None, project_id: str = "") -> None:
        self._client = secret_client
        self._project_id = project_id

    def _secret_name(self, tenant_id: str, brand_id: str, canal: str) -> str:
        """Constrói o nome do secret no formato escopado."""
        return f"{tenant_id}--{brand_id}--{canal}--credentials"

    async def get_credentials(self, tenant_id: str, brand_id: str, canal: str) -> dict[str, str]:
        """Busca credenciais do Secret Manager.

        Retorna dict com os tokens/chaves necessários para o adapter do canal.
        Ex: {"access_token": "...", "page_id": "...", "ig_user_id": "..."}
        """
        secret_id = self._secret_name(tenant_id, brand_id, canal)

        if self._client is None:
            # Modo stub para desenvolvimento/testes
            raise RuntimeError(
                f"Secret Manager client não configurado. "
                f"Não é possível resolver credenciais para '{secret_id}'."
            )

        # Acessa a versão mais recente do secret
        name = f"projects/{self._project_id}/secrets/{secret_id}/versions/latest"
        response = self._client.access_secret_version(request={"name": name})
        payload = response.payload.data.decode("utf-8")
        return json.loads(payload)
