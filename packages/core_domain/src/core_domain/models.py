"""Tipos de domínio — doc 11 §3. Modelos imutáveis (Pydantic v2)."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from core_domain.enums import (
    Autonomia,
    Canal,
    CostAccount,
    Funil,
    ItemStatus,
    PlatformStatus,
)

# --- Scope (presente em TODA entidade de tenant, doc 09 §2) ---


class Scope(BaseModel):
    """Identidade de escopo — toda entidade de tenant carrega isto."""

    tenant_id: str
    brand_id: str


# --- Tipos auxiliares ---


class Fonte(BaseModel):
    tipo: str  # pauta | video | noticia_ainewz
    ref: str | None = None  # content_atom_id | noticia_id


class Artefatos(BaseModel):
    texto: str | None = None  # gs://...
    imagens: list[str] = Field(default_factory=list)
    video: str | None = None


class EventoProducao(BaseModel):
    agente: str
    acao: str
    custo_brl: float = 0.0
    ts: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Performance(BaseModel):
    views: int = 0
    retencao_pct: float = 0.0
    ctr: float = 0.0
    saves: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    atualizado_em: datetime | None = None


class RiscoSensibilidade(BaseModel):
    """Guardrail de temas sensíveis — doc 08 §3b."""

    nivel: str  # baixo | medio | alto
    tipo: str  # intencional | acidental
    publico_em_risco: str
    diagnostico: str


# --- Entidades principais ---


class BacklogItem(BaseModel):
    id: str
    scope: Scope
    tipo: str
    pilar: str
    funil: Funil
    fonte: Fonte
    requer_ceo: bool = False
    status: ItemStatus = ItemStatus.IDEIA
    slot_alvo: str | None = None
    referencias_grafo: list[str] = Field(default_factory=list)
    artefatos: Artefatos = Field(default_factory=Artefatos)
    risco_sensibilidade: RiscoSensibilidade | None = None
    historico: list[EventoProducao] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ContentNode(BaseModel):
    """Grafo de conteúdo — doc 02 + doc 10 §6."""

    id: str
    scope: Scope
    titulo: str
    conceitos: list[str]
    depende_de: list[str] = Field(default_factory=list)
    pilar: str
    funil: Funil
    formato: str
    canal: Canal
    url: str | None = None
    como_referenciar: dict[str, str] = Field(default_factory=dict)
    template_id: str | None = None
    template_versao: str | None = None
    assets_usados: list[str] = Field(default_factory=list)
    performance: Performance = Field(default_factory=Performance)
    few_shot_aprovado: bool = False
    embedding: list[float] | None = None
    publicado_em: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class MediaAsset(BaseModel):
    """Acervo de mídia — doc 10 §4."""

    id: str
    scope: Scope
    tipo: str  # imagem | video | logo
    fonte: str  # humano_upload | agente_pesquisa | ainewz_noticia | video_ia_futuro
    url: str
    tags: list[str] = Field(default_factory=list)
    descricao: str = ""
    embedding: list[float] | None = None
    ref_origem: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Slot(BaseModel):
    """Posição no calendário — doc 02."""

    id: str
    scope: Scope
    canal: Canal
    dia: str  # ISO date
    hora: str  # HH:MM
    pilar: str
    funil: Funil
    item: str | None = None  # BacklogItem.id
    origem_hora: str = "default"  # learning-XXXX | default
    status: str = "vago"  # vago | reservado | publicado


class CostEntry(BaseModel):
    """Entrada no ledger de custo — doc 05 §2."""

    id: str
    scope: Scope
    ts: datetime = Field(default_factory=lambda: datetime.now(UTC))
    agente: str
    item: str | None = None
    conta: CostAccount = CostAccount.OPERACAO
    servico: str  # vertex_llm | vertex_embedding | cloud_run_render | storage | outro
    modelo: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    custo_estimado_brl: float = 0.0


class BrandConfig(BaseModel):
    """Brand profile carregado do Firestore — doc 04."""

    brand_id: str
    nome: str
    missao: str
    idioma: str = "pt-BR"
    modo: str = "sandbox"  # sandbox | producao
    nivel_de_franqueza: float = 0.9
    buffer_minimo_dias: int = 7
    estrategia_ativa: str = ""  # path da versão ativa


class TenantConfig(BaseModel):
    """Configuração do tenant — doc 02/05."""

    tenant_id: str
    platform_status: PlatformStatus = PlatformStatus.ATIVO
    budget_mensal_brl: float = 600.0
    gasto_mes_ledger_brl: float = 0.0


class TeamSubscription(BaseModel):
    """Time contratado/ativo — doc 09 §3."""

    team_id: str
    ativo: bool = False
    obrigatorio: bool = False


class ChannelConfig(BaseModel):
    """Configuração de canal por marca — extraída do brand profile."""

    canal: Canal
    ativo: bool = True
    autonomia: Autonomia = Autonomia.APPROVE_REQUIRED
    janelas: list[str] = Field(default_factory=list)
    formatos: list[str] = Field(default_factory=list)
