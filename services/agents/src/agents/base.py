"""PlatformAgent — base de todo agente (doc 11 §4.1).

Garante: escopo de tenant, gateway de LLM (nunca Vertex direto),
e acesso ao KB/memória. A lógica específica vive em handle().
"""

from abc import ABC, abstractmethod
from typing import Any

from core_domain import AgentRequest, AgentResponse, Scope, TaskKind
from core_domain.models import BrandConfig
from llm_gateway import LlmGateway


class PlatformAgent(ABC):
    """Base abstrata de todo agente da plataforma.

    Regras:
    - Todo prompt monta contexto a partir de config+KB+grafo — NUNCA hardcode de marca
    - Chamadas LLM só via self._gateway (nunca Vertex direto)
    - Escopo de tenant sempre presente
    """

    agent_id: str
    team: str  # doc 09 §3 — a qual time pertence

    def __init__(self, gateway: LlmGateway, repo: Any, kb: Any = None) -> None:
        self._gateway = gateway
        self._repo = repo  # ScopedRepository (tipado na implementação)
        self._kb = kb  # KnowledgeBase (marketing_kb + learnings)

    @abstractmethod
    async def handle(self, req: AgentRequest) -> AgentResponse:
        """Processa uma tarefa e retorna resultado.

        Implementação por agente. REGRA: todo prompt monta contexto
        a partir de config+KB+grafo — NUNCA hardcode de marca.
        """
        ...

    async def _call_llm(
        self,
        scope: Scope,
        task_kind: TaskKind,
        messages: list[dict[str, str]],
        item_id: str | None = None,
    ) -> str:
        """Helper: chama LLM via gateway (nunca direto)."""
        result = await self._gateway.complete(
            scope=scope,
            agent_id=self.agent_id,
            task_kind=task_kind,
            messages=messages,
            item_id=item_id,
        )
        return result.text

    async def _get_brand_config(self, scope: Scope) -> BrandConfig:
        """Carrega o brand profile do escopo atual."""
        brand = await self._repo.get(scope.brand_id)
        if brand is None:
            return BrandConfig(brand_id=scope.brand_id, nome="", missao="")
        return brand
