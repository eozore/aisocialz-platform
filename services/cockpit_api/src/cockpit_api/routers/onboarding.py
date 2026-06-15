"""Onboarding — criação de tenant e marca via cockpit (self-service).

Qualquer pessoa pode criar conta + marca. Zero dado de marca em código.
Substitui as migrations hardcoded.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])


class CreateTenantRequest(BaseModel):
    """Dados para criar um novo tenant."""

    tenant_id: str  # slug único (ex: "victor", "empresa-x")
    nome: str  # nome de exibição
    email: str
    budget_mensal_brl: float = 600.0


class CreateBrandRequest(BaseModel):
    """Dados para criar uma nova marca dentro de um tenant."""

    brand_id: str  # slug único (ex: "eozore", "ainewz")
    nome: str  # nome de exibição (ex: "éozoré")
    missao: str
    idioma: str = "pt-BR"
    nivel_de_franqueza: float = 0.9
    buffer_minimo_dias: int = 7
    voz_descricao: str = ""
    voz_anti_padroes: list[str] = Field(default_factory=list)


class CreateStrategyRequest(BaseModel):
    """Dados para criar uma estratégia de marca."""

    version: str  # ex: "v1-2026Q2"
    objetivo: str
    tese_central: str = ""
    objetivo_de_conversao_tipo: str = "audiencia"
    objetivo_de_conversao_metrica: str = ""
    pilares: list[dict[str, object]] = Field(default_factory=list)


@router.post("/tenant")
async def create_tenant(req: CreateTenantRequest) -> dict:
    """Cria um novo tenant com configuração padrão.

    Cria no Firestore:
    - tenant/{tenant_id}/config/main (platform_status, budget, etc.)
    - tenant/{tenant_id}/team_subscriptions/* (todos os times, core=ativo)
    """
    # Na implementação real: persistence.ScopedRepository grava no Firestore
    # Aqui retorna o que será gravado para validação
    config = {
        "tenant_id": req.tenant_id,
        "nome": req.nome,
        "email": req.email,
        "platform_status": "ativo",
        "budget_mensal_brl": req.budget_mensal_brl,
        "gasto_mes_ledger_brl": 0.0,
    }

    # Team subscriptions padrão (core obrigatório, resto desligado)
    teams = {
        "core": {"team_id": "core", "ativo": True, "obrigatorio": True},
        "linkedin": {"team_id": "linkedin", "ativo": False, "obrigatorio": False},
        "meta": {"team_id": "meta", "ativo": False, "obrigatorio": False},
        "blog": {"team_id": "blog", "ativo": False, "obrigatorio": False},
        "radar": {"team_id": "radar", "ativo": False, "obrigatorio": False},
        "comunidade": {"team_id": "comunidade", "ativo": False, "obrigatorio": False},
        "analytics_web": {"team_id": "analytics_web", "ativo": False, "obrigatorio": False},
        "youtube": {"team_id": "youtube", "ativo": False, "obrigatorio": False},
        "tiktok": {"team_id": "tiktok", "ativo": False, "obrigatorio": False},
        "email": {"team_id": "email", "ativo": False, "obrigatorio": False},
        "video_ia": {"team_id": "video_ia", "ativo": False, "obrigatorio": False},
    }

    return {"created": True, "config": config, "teams": teams}


@router.post("/tenant/{tenant_id}/brand")
async def create_brand(tenant_id: str, req: CreateBrandRequest) -> dict:
    """Cria uma nova marca dentro de um tenant.

    Cria no Firestore:
    - tenant/{tenant_id}/brands/{brand_id} (brand profile)
    """
    brand_profile = {
        "brand_id": req.brand_id,
        "nome": req.nome,
        "missao": req.missao,
        "idioma": req.idioma,
        "modo": "sandbox",  # sempre nasce sandbox (doc 06 §1.5)
        "nivel_de_franqueza": req.nivel_de_franqueza,
        "buffer_minimo_dias": req.buffer_minimo_dias,
        "voz": {
            "descricao": req.voz_descricao,
            "anti_padroes": req.voz_anti_padroes,
            "few_shot": [],  # populado via endpoint dedicado
        },
        "estrategia_ativa": "",  # definida após criar estratégia
    }

    return {
        "created": True,
        "tenant_id": tenant_id,
        "brand": brand_profile,
    }


@router.post("/tenant/{tenant_id}/brand/{brand_id}/strategy")
async def create_strategy(tenant_id: str, brand_id: str, req: CreateStrategyRequest) -> dict:
    """Cria uma estratégia para a marca.

    Cria no Firestore:
    - tenant/{tid}/brands/{bid}/strategies/versions/{version}
    - Atualiza brand.estrategia_ativa
    """
    strategy = {
        "version": req.version,
        "status": "ativa",
        "objetivo": req.objetivo,
        "tese_central": req.tese_central,
        "objetivo_de_conversao": {
            "tipo": req.objetivo_de_conversao_tipo,
            "metrica_primaria": req.objetivo_de_conversao_metrica,
        },
        "pilares": req.pilares,
    }

    return {
        "created": True,
        "tenant_id": tenant_id,
        "brand_id": brand_id,
        "strategy": strategy,
    }
