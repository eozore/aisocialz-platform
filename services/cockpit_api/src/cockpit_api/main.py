"""svc-cockpit-api — BFF do cockpit Next.js (doc 11 §9).

O cockpit nunca toca Firestore nem agentes direto — fala só com este BFF.
Toda rota injeta tenant_id do token de auth (nunca do corpo).
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from cockpit_api.routers.connections import router as connections_router
from cockpit_api.routers.onboarding import router as onboarding_router
from cockpit_api.routers.voice import router as voice_router

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

# Registra routers
app.include_router(onboarding_router)
app.include_router(connections_router)
app.include_router(voice_router)

# V1: tenant fixo até implementar auth. Na virada SaaS, extraído do token JWT.
DEFAULT_TENANT = "default"


def _get_tenant(request: Request) -> str:
    """Extrai tenant_id do auth. V1: retorna default."""
    # TODO: extrair do token JWT quando auth for implementado
    return DEFAULT_TENANT


# --- Endpoints normativos V1 (doc 11 §9) ---


@app.get("/api/brands")
async def get_brands(request: Request) -> dict:
    """Marcas do tenant + status."""

    # Na V1: retorna marcas configuradas via onboarding
    # Por agora: retorna placeholder para demonstrar o cockpit
    return {
        "tenant_id": _get_tenant(request),
        "brands": [
            {
                "brand_id": "minha-marca",
                "nome": "Minha Marca",
                "modo": "sandbox",
                "status": "ativo",
                "canais_conectados": 0,
                "nota": "Crie sua marca via /api/onboarding",
            }
        ],
    }


@app.get("/api/backlog")
async def get_backlog(
    request: Request, status: str | None = None, brand: str | None = None
) -> dict:
    """Esteira de produção (doc 09 §5)."""
    return {
        "items": [
            {
                "id": "demo-001",
                "tipo": "post_linkedin",
                "pilar": "estratégia de conteúdo",
                "funil": "topo",
                "status": "producao",
                "agente_atual": "redator",
                "canal": "linkedin",
            },
            {
                "id": "demo-002",
                "tipo": "carrossel",
                "pilar": "fundamentos",
                "funil": "meio",
                "status": "revisao",
                "agente_atual": "revisor",
                "canal": "instagram",
            },
            {
                "id": "demo-003",
                "tipo": "thread",
                "pilar": "bastidores",
                "funil": "topo",
                "status": "aprovado",
                "agente_atual": None,
                "canal": "threads",
            },
        ],
        "filters": {"status": status, "brand": brand},
    }


@app.get("/api/approvals")
async def get_approvals(request: Request) -> dict:
    """Fila do CEO."""
    return {
        "approvals": [
            {
                "id": "aprov-001",
                "tipo": "item",
                "resumo": "Post LinkedIn sobre estratégia de conteúdo — aguardando sua aprovação",
                "prazo": "2026-06-15",
                "fallback": "aplicar",
            }
        ],
    }


@app.post("/api/approvals/{approval_id}")
async def respond_approval(approval_id: str, request: Request) -> dict:
    """Aprovar/editar/rejeitar item da fila."""
    return {"approval_id": approval_id, "nota": "Stub — gravar decision_log"}


@app.get("/api/schedule")
async def get_schedule(
    request: Request, brand: str | None = None, semana: str | None = None
) -> dict:
    """Calendário."""
    return {
        "slots": [
            {"dia": "2026-06-16", "hora": "08:30", "canal": "linkedin", "pilar": "estratégia", "formato": "post_linkedin", "status": "reservado"},
            {"dia": "2026-06-16", "hora": "12:00", "canal": "instagram", "pilar": "fundamentos", "formato": "carrossel", "status": "reservado"},
            {"dia": "2026-06-17", "hora": "13:00", "canal": "threads", "pilar": "bastidores", "formato": "thread", "status": "vago"},
            {"dia": "2026-06-18", "hora": "08:30", "canal": "linkedin", "pilar": "mercado", "formato": "post_linkedin", "status": "vago"},
            {"dia": "2026-06-18", "hora": "07:00", "canal": "blog", "pilar": "fundamentos", "formato": "blog", "status": "vago"},
        ],
        "brand": brand,
        "semana": semana,
    }


@app.get("/api/teams")
async def get_teams(request: Request) -> dict:
    """Team subscriptions (sala de contratação)."""
    return {
        "teams": [
            {"team_id": "core", "nome": "Core (Diretor, Estrategista, Revisor, Analista)", "ativo": True, "obrigatorio": True},
            {"team_id": "linkedin", "nome": "LinkedIn", "ativo": True, "obrigatorio": False},
            {"team_id": "meta", "nome": "Meta (Instagram + Facebook + Threads)", "ativo": True, "obrigatorio": False},
            {"team_id": "blog", "nome": "Blog", "ativo": True, "obrigatorio": False},
            {"team_id": "radar", "nome": "Radar (Contexto)", "ativo": True, "obrigatorio": False},
            {"team_id": "comunidade", "nome": "Comunidade", "ativo": False, "obrigatorio": False},
            {"team_id": "youtube", "nome": "YouTube", "ativo": False, "obrigatorio": False},
            {"team_id": "tiktok", "nome": "TikTok", "ativo": False, "obrigatorio": False},
        ],
    }


@app.post("/api/teams/{team_id}")
async def toggle_team(team_id: str, request: Request) -> dict:
    """Ativar/desativar time."""
    return {"team_id": team_id, "nota": "Stub"}


@app.get("/api/cost")
async def get_cost(request: Request) -> dict:
    """Gasto do mês vs gatilhos (doc 05 §5)."""
    return {
        "gasto_mes_brl": 12.45,
        "orcamento_mensal_brl": 600.0,
        "platform_status": "ativo",
        "projecao_fim_mes_brl": 85.0,
        "gatilhos": [
            {"valor": 200, "modo": "aviso"},
            {"valor": 400, "modo": "economia"},
            {"valor": 600, "modo": "bloqueado"},
        ],
        "top_consumidores": [
            {"agente": "redator", "custo_brl": 5.20},
            {"agente": "estrategista", "custo_brl": 3.10},
            {"agente": "revisor", "custo_brl": 2.80},
            {"agente": "curador", "custo_brl": 1.35},
        ],
    }


@app.post("/api/chat/diretor")
async def chat_diretor(request: Request) -> dict:
    """Mensagem ao Diretor-conselheiro via Vertex AI (Gemini 2.5 Flash)."""
    from google import genai

    body = await request.json()
    mensagem = body.get("mensagem", "")

    if not mensagem:
        return {"resposta": "Envie uma mensagem para conversar com o Diretor."}

    system_prompt = (
        "Você é o Diretor de Marketing (CMO de IA) desta plataforma. "
        "Converse em linguagem de negócio com o CEO. "
        "Recomende com candor — discorde quando o pedido fere a estratégia. "
        "Nunca abra com elogio. Seja direto, útil e estratégico. "
        "Responda em português brasileiro. "
        "Use o formato: POSIÇÃO + EVIDÊNCIA + CONTRA-ARGUMENTO + CONFIANÇA "
        "quando fizer recomendações estruturadas."
    )

    try:
        client = genai.Client(
            vertexai=True, project="aisocialz-project", location="us-central1"
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=mensagem,
            config={"system_instruction": system_prompt, "max_output_tokens": 2048},
        )
        return {
            "resposta": response.text,
            "modelo": "gemini-2.5-flash",
        }
    except Exception as e:
        return {"resposta": f"Erro ao consultar o Diretor: {e}", "erro": True}


@app.get("/api/media")
async def get_media(request: Request, brand: str | None = None) -> dict:
    """Acervo de mídia — organizado por categoria + dimensão."""
    return {
        "brand": brand,
        "kit_de_marca": {
            "cores": [],
            "fontes": [],
            "logos": [],
            "elementos_graficos": [],
            "nota": "Configure via POST /api/onboarding ou cockpit",
        },
        "categorias": [
            {"id": "logo", "nome": "Logos", "total": 0},
            {"id": "icone", "nome": "Ícones", "total": 0},
            {"id": "background", "nome": "Backgrounds", "total": 0},
            {"id": "foto", "nome": "Fotos", "total": 0},
            {"id": "ilustracao", "nome": "Ilustrações", "total": 0},
            {"id": "pattern", "nome": "Patterns", "total": 0},
            {"id": "elemento_grafico", "nome": "Elementos Gráficos", "total": 0},
            {"id": "video", "nome": "Vídeos", "total": 0},
        ],
        "dimensoes_disponiveis": [
            {"id": "1080x1920", "uso": "Stories / Reels"},
            {"id": "1080x1350", "uso": "Feed IG / LinkedIn"},
            {"id": "1080x1080", "uso": "Post quadrado"},
            {"id": "1280x720", "uso": "Thumbnail YouTube"},
            {"id": "1500x500", "uso": "Header LinkedIn"},
            {"id": "1200x628", "uso": "Link preview / OG image"},
            {"id": "original", "uso": "Tamanho original"},
        ],
        "assets": [],
    }


@app.get("/api/connections")
async def get_connections(request: Request, brand: str | None = None) -> dict:
    """Status de credenciais por canal."""
    return {"canais": [], "brand": brand}


@app.get("/api/templates")
async def get_templates(request: Request, brand: str | None = None) -> dict:
    """Template Studio — organizado por formato e canal."""
    return {
        "brand": brand,
        "formatos": [
            {
                "formato": "carrossel",
                "canais": ["instagram", "linkedin"],
                "dimensoes": "1080x1350",
                "templates": [
                    {"id": "base_tipografico", "nome": "Tipográfico", "status": "aprovado", "versao": "1.0.0"},
                    {"id": "base_com_imagem", "nome": "Com imagem", "status": "aprovado", "versao": "1.0.0"},
                    {"id": "base_dado", "nome": "Card de dado", "status": "sandbox", "versao": "0.1.0"},
                ],
            },
            {
                "formato": "card",
                "canais": ["instagram", "threads"],
                "dimensoes": "1080x1350",
                "templates": [
                    {"id": "base_noticia", "nome": "Card de notícia", "status": "aprovado", "versao": "1.0.0"},
                    {"id": "base_citacao", "nome": "Card de citação", "status": "sandbox", "versao": "0.1.0"},
                ],
            },
            {
                "formato": "thumbnail",
                "canais": ["youtube"],
                "dimensoes": "1280x720",
                "templates": [
                    {"id": "base_thumbnail", "nome": "Thumbnail padrão", "status": "sandbox", "versao": "0.1.0"},
                ],
            },
            {
                "formato": "stories",
                "canais": ["instagram"],
                "dimensoes": "1080x1920",
                "templates": [
                    {"id": "base_story", "nome": "Story padrão", "status": "sandbox", "versao": "0.1.0"},
                ],
            },
        ],
    }
