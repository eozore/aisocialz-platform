"""Contratos de mensagem entre agentes — doc 11 §4.2."""

from pydantic import BaseModel, Field

from core_domain.models import Scope


class AgentRequest(BaseModel):
    """Mensagem de entrada para qualquer agente."""

    request_id: str
    scope: Scope
    task: str  # "produzir_post" | "revisar" | "pontuar_noticia" | ...
    item_id: str | None = None
    payload: dict[str, object] = Field(default_factory=dict)
    trace_id: str = ""


class AgentResponse(BaseModel):
    """Resposta de qualquer agente."""

    request_id: str
    ok: bool
    output: dict[str, object] = Field(default_factory=dict)
    cost_brl: float = 0.0
    next: list[AgentRequest] = Field(default_factory=list)
    notes: str | None = None
