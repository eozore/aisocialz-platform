"""Enums de domínio — doc 11 §3."""

from enum import StrEnum


class Canal(StrEnum):
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    THREADS = "threads"
    BLOG = "blog"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"


class Funil(StrEnum):
    TOPO = "topo"
    MEIO = "meio"
    FUNDO = "fundo"


class ItemStatus(StrEnum):
    IDEIA = "ideia"
    BRIEFING = "briefing"
    PRODUCAO = "producao"
    REVISAO = "revisao"
    AGUARDANDO_CEO = "aguardando_ceo"
    APROVADO = "aprovado"
    AGENDADO = "agendado"
    PUBLICADO = "publicado"
    REJEITADO = "rejeitado"
    QUARENTENA = "quarentena"


class Autonomia(StrEnum):
    DRAFT_ONLY = "draft_only"
    APPROVE_REQUIRED = "approve_required"
    AUTO_PUBLISH = "auto_publish"


class PlatformStatus(StrEnum):
    ATIVO = "ativo"
    ECONOMIA = "economia"
    PAUSED = "paused"


class TaskKind(StrEnum):
    """Natureza da tarefa para routing de modelo — doc 03 §1."""

    ESTRUTURAL = "estrutural"
    ANALITICA = "analitica"
    CRIATIVA = "criativa"
    CONSELHO = "conselho"
    EMBEDDING = "embedding"


class CostAccount(StrEnum):
    """Conta de custo — doc 08 §7. Só 'operacao' dispara gatilhos."""

    OPERACAO = "operacao"
    BUILD = "build"


class TeamId(StrEnum):
    CORE = "core"
    LINKEDIN = "linkedin"
    META = "meta"
    BLOG = "blog"
    RADAR = "radar"
    COMUNIDADE = "comunidade"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    ANALYTICS_WEB = "analytics_web"
    EMAIL = "email"
    VIDEO_IA = "video_ia"
