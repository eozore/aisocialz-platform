"""Tipos de request/response do serviço de render — doc 11 §8.2, doc 07."""

from pydantic import BaseModel, Field

from core_domain import Scope


class RenderRequest(BaseModel):
    """Requisição de render — enviada ao svc-render."""

    scope: Scope
    template_id: str
    template_versao: str
    formato: str  # carrossel | card | thumbnail | reel_render | ...
    dados: dict[str, object] = Field(default_factory=dict)  # variáveis do template
    assets: list[str] = Field(default_factory=list)  # gs:// de imagens do acervo
    saida: str = "png"  # png | jpg | mp4
    dimensoes: tuple[int, int] = (1080, 1350)


class RenderResult(BaseModel):
    """Resultado de um render."""

    ok: bool
    outputs: list[str] = Field(default_factory=list)  # gs:// dos arquivos gerados
    overflow_detectado: bool = False
    custo_brl: float = 0.0
    erro: str | None = None
