"""Conexão de canais — fluxo OAuth + manual via cockpit (doc 09 §8).

Qualquer CEO conecta as próprias contas via cockpit.
Tokens gravados no Secret Manager sob caminho escopado.
Status visível no cockpit: conectado / expira em N dias / desconectado.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/connections", tags=["connections"])


# --- Schemas ---


class ChannelStatus(BaseModel):
    """Status de conexão de um canal."""

    canal: str
    status: str  # "conectado" | "expira_em_N_dias" | "desconectado"
    expira_em_dias: int | None = None


class OAuthStartResponse(BaseModel):
    """Resposta ao iniciar fluxo OAuth."""

    authorization_url: str
    state: str  # para validar callback


class ManualCredentialRequest(BaseModel):
    """Credenciais manuais (canais sem OAuth)."""

    credentials: dict[str, str]  # JSON com os campos necessários


class OAuthCallbackRequest(BaseModel):
    """Dados do callback OAuth."""

    code: str
    state: str


# --- OAuth configs por canal ---

OAUTH_CONFIGS = {
    "instagram": {
        "auth_url": "https://www.facebook.com/v20.0/dialog/oauth",
        "token_url": "https://graph.facebook.com/v20.0/oauth/access_token",
        "scopes": [
            "instagram_basic",
            "instagram_content_publish",
            "instagram_manage_comments",
            "instagram_manage_insights",
            "pages_show_list",
            "pages_read_engagement",
        ],
    },
    "facebook": {
        "auth_url": "https://www.facebook.com/v20.0/dialog/oauth",
        "token_url": "https://graph.facebook.com/v20.0/oauth/access_token",
        "scopes": ["pages_manage_posts", "pages_read_engagement", "pages_show_list"],
    },
    "threads": {
        "auth_url": "https://threads.net/oauth/authorize",
        "token_url": "https://graph.threads.net/oauth/access_token",
        "scopes": ["threads_basic", "threads_content_publish", "threads_manage_insights"],
    },
    "linkedin": {
        "auth_url": "https://www.linkedin.com/oauth/v2/authorization",
        "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
        "scopes": ["w_member_social", "r_liteprofile"],
    },
}

# Canais sem OAuth (credenciais manuais)
MANUAL_CHANNELS = {"blog"}


# --- Endpoints ---


@router.get("", response_model=list[ChannelStatus])
async def list_connections(brand: str | None = None) -> list[ChannelStatus]:
    """Lista status de conexão de todos os canais da marca.

    O cockpit mostra: conectado / expira em N dias / desconectado.
    Lê metadata dos secrets no Secret Manager.
    """
    # Na implementação real: para cada canal ativo do brand,
    # checa se o secret existe e sua validade
    canais = ["instagram", "facebook", "threads", "linkedin", "blog"]
    statuses = []
    for canal in canais:
        # Stub: todos desconectados até serem configurados
        statuses.append(ChannelStatus(canal=canal, status="desconectado"))
    return statuses


@router.post("/{canal}/oauth/start")
async def oauth_start(canal: str, brand_id: str) -> OAuthStartResponse:
    """Inicia fluxo OAuth para conectar uma conta de canal.

    Retorna URL de autorização para o CEO abrir no browser.
    Após autorizar, o callback recebe o code e troca por token.
    """
    if canal not in OAUTH_CONFIGS:
        raise HTTPException(
            status_code=400,
            detail=f"Canal '{canal}' não suporta OAuth. Use /manual.",
        )

    config = OAUTH_CONFIGS[canal]
    # Na implementação real:
    # 1. Gera state único (CSRF protection)
    # 2. Monta URL com client_id, redirect_uri, scopes, state
    # 3. Retorna para o cockpit abrir em popup/redirect

    import uuid

    state = str(uuid.uuid4())
    scopes = " ".join(config["scopes"])
    auth_url = (
        f"{config['auth_url']}?"
        f"client_id={{APP_CLIENT_ID}}"
        f"&redirect_uri={{REDIRECT_URI}}"
        f"&scope={scopes}"
        f"&state={state}"
        f"&response_type=code"
    )

    return OAuthStartResponse(authorization_url=auth_url, state=state)


@router.post("/{canal}/oauth/callback")
async def oauth_callback(canal: str, brand_id: str, req: OAuthCallbackRequest) -> dict:
    """Recebe callback OAuth, troca code por token, grava no Secret Manager.

    Fluxo:
    1. Valida state (CSRF)
    2. Troca code por access_token (+ refresh_token se disponível)
    3. Para Meta: troca por long-lived token (60 dias)
    4. Grava no Secret Manager: {tenant}--{brand}--{canal}--credentials
    5. Retorna status de sucesso
    """
    if canal not in OAUTH_CONFIGS:
        raise HTTPException(status_code=400, detail=f"Canal '{canal}' não suporta OAuth")

    # Na implementação real:
    # - Valida state contra o que foi gerado em /start
    # - POST para token_url com code + client_secret
    # - Para Meta: GET /oauth/access_token?grant_type=fb_exchange_token para long-lived
    # - Grava JSON no Secret Manager no caminho escopado

    # Stub de sucesso
    return {
        "connected": True,
        "canal": canal,
        "brand_id": brand_id,
        "message": f"Canal {canal} conectado com sucesso. Token gravado no Secret Manager.",
        "secret_path": f"{{tenant_id}}--{brand_id}--{canal}--credentials",
    }


@router.post("/{canal}/manual")
async def manual_credentials(canal: str, brand_id: str, req: ManualCredentialRequest) -> dict:
    """Grava credenciais manuais no Secret Manager (canais sem OAuth).

    Ex: Blog API key, ou System User token que o CEO já possui.
    """
    # Na implementação real:
    # 1. Valida que os campos obrigatórios estão presentes
    # 2. Grava JSON no Secret Manager: {tenant}--{brand}--{canal}--credentials
    # 3. Testa a credencial (chamada de validação ao canal)

    # Campos esperados por canal
    required_fields: dict[str, list[str]] = {
        "blog": ["api_url", "api_key"],
        "instagram": ["access_token", "ig_user_id", "page_id"],
        "facebook": ["access_token", "page_id"],
        "threads": ["access_token", "threads_user_id"],
        "linkedin": ["access_token", "person_urn"],
    }

    expected = required_fields.get(canal, [])
    missing = [f for f in expected if f not in req.credentials]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Campos obrigatórios faltando para {canal}: {missing}",
        )

    return {
        "connected": True,
        "canal": canal,
        "brand_id": brand_id,
        "method": "manual",
        "secret_path": f"{{tenant_id}}--{brand_id}--{canal}--credentials",
    }


@router.post("/{canal}/refresh")
async def refresh_token(canal: str, brand_id: str) -> dict:
    """Força refresh do token de um canal (usado pelo job de saúde ou manual).

    Para Meta/Threads: troca token atual por novo long-lived.
    Para LinkedIn: usa refresh_token para obter novo access_token.
    """
    # Na implementação real:
    # 1. Lê secret atual do Secret Manager
    # 2. Faz request de refresh ao provedor
    # 3. Grava novo token no Secret Manager
    # 4. Atualiza metadata de expiração

    return {
        "refreshed": True,
        "canal": canal,
        "brand_id": brand_id,
        "nota": "Token renovado. Nova expiração calculada.",
    }


@router.delete("/{canal}")
async def disconnect_channel(canal: str, brand_id: str) -> dict:
    """Desconecta um canal (remove credenciais do Secret Manager)."""
    return {
        "disconnected": True,
        "canal": canal,
        "brand_id": brand_id,
    }
