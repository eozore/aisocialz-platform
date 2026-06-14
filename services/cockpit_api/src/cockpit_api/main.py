"""svc-cockpit-api — BFF do cockpit Next.js (doc 11 §9).

O cockpit nunca toca Firestore nem agentes direto — fala só com este BFF.
Toda rota injeta tenant_id do token de auth (nunca do corpo).
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AISocialZ Cockpit API",
    description="BFF para o cockpit Next.js — endpoints normativos da V1",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restringir em produção
    allow_methods=["*"],
    allow_headers=["*"],
)

# V1: tenant fixo (Victor). Na virada SaaS, extraído do token JWT.
DEFAULT_TENANT = "victor"


def _get_tenant(request: Request) -> str:
    """Extrai tenant_id do auth. V1: retorna default."""
    # TODO: extrair do token JWT quando auth for implementado
    return DEFAULT_TENANT


# --- Endpoints normativos V1 (doc 11 §9) ---


@app.get("/api/brands")
async def get_brands(request: Request) -> dict:
    """Marcas do tenant + status."""
    return {"tenant_id": _get_tenant(request), "brands": [], "nota": "Stub — conectar persistence"}


@app.get("/api/backlog")
async def get_backlog(
    request: Request, status: str | None = None, brand: str | None = None
) -> dict:
    """Esteira de produção (doc 09 §5)."""
    return {"items": [], "filters": {"status": status, "brand": brand}}


@app.get("/api/approvals")
async def get_approvals(request: Request) -> dict:
    """Fila do CEO."""
    return {"approvals": []}


@app.post("/api/approvals/{approval_id}")
async def respond_approval(approval_id: str, request: Request) -> dict:
    """Aprovar/editar/rejeitar item da fila."""
    return {"approval_id": approval_id, "nota": "Stub — gravar decision_log"}


@app.get("/api/schedule")
async def get_schedule(
    request: Request, brand: str | None = None, semana: str | None = None
) -> dict:
    """Calendário."""
    return {"slots": [], "brand": brand, "semana": semana}


@app.get("/api/teams")
async def get_teams(request: Request) -> dict:
    """Team subscriptions (sala de contratação)."""
    return {"teams": []}


@app.post("/api/teams/{team_id}")
async def toggle_team(team_id: str, request: Request) -> dict:
    """Ativar/desativar time."""
    return {"team_id": team_id, "nota": "Stub"}


@app.get("/api/cost")
async def get_cost(request: Request) -> dict:
    """Gasto do mês vs gatilhos (doc 05 §5)."""
    return {
        "gasto_mes_brl": 0.0,
        "orcamento_mensal_brl": 600.0,
        "platform_status": "ativo",
        "gatilhos": [
            {"valor": 200, "modo": "aviso"},
            {"valor": 400, "modo": "economia"},
            {"valor": 600, "modo": "bloqueado"},
        ],
    }


@app.post("/api/chat/diretor")
async def chat_diretor(request: Request) -> dict:
    """Mensagem ao Diretor-conselheiro."""
    return {"resposta": "Stub — conectar ao DiretorAgent"}


@app.get("/api/media")
async def get_media(request: Request, brand: str | None = None) -> dict:
    """Acervo de mídia."""
    return {"assets": [], "brand": brand}


@app.get("/api/connections")
async def get_connections(request: Request, brand: str | None = None) -> dict:
    """Status de credenciais por canal."""
    return {"canais": [], "brand": brand}


@app.get("/api/templates")
async def get_templates(request: Request, brand: str | None = None) -> dict:
    """Template Studio (galeria)."""
    return {"templates": [], "brand": brand}
