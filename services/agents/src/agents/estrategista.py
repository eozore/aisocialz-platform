"""Estrategista — decide O QUE e QUANDO (doc 03 §3).

A partir de missão+público, nunca de "o que existe pronto".
Reserva ~20% dos slots para experimentos do Analista.

Modelo: Pro/Sonnet
Time: core (obrigatório)
Candor obrigatório.
"""

from agents.base import PlatformAgent
from core_domain import AgentRequest, AgentResponse, Scope, TaskKind


class EstrategistaAgent(PlatformAgent):
    agent_id = "estrategista"
    team = "core"

    async def handle(self, req: AgentRequest) -> AgentResponse:
        """Gera calendário semanal ou aloca slot.

        Tasks suportadas:
        - "planejar_semana": gera calendário semanal completo
        - "alocar_slot": aloca um item específico a um slot
        """
        task = req.task
        scope = req.scope

        if task == "planejar_semana":
            return await self._planejar_semana(scope, req)
        elif task == "alocar_slot":
            return await self._alocar_slot(scope, req)
        else:
            return AgentResponse(
                request_id=req.request_id,
                ok=False,
                output={"erro": f"Task '{task}' não suportada pelo Estrategista"},
            )

    async def _planejar_semana(self, scope: Scope, req: AgentRequest) -> AgentResponse:
        """Planeja calendário semanal com slots, pilares e formatos."""
        messages = [
            {
                "role": "system",
                "content": (
                    "Você é o Estrategista. Decida O QUE e QUANDO publicar esta semana. "
                    "Use o formato de candor: POSIÇÃO + EVIDÊNCIA + CONTRA-ARGUMENTO + CONFIANÇA. "
                    "Reserve ~20% dos slots para experimentos. "
                    "Nunca decida a partir do que já existe pronto — decida pela estratégia."
                ),
            },
            {
                "role": "user",
                "content": "Gere o planejamento semanal com base na estratégia ativa.",
            },
        ]

        resposta = await self._call_llm(scope, TaskKind.ANALITICA, messages)

        return AgentResponse(
            request_id=req.request_id,
            ok=True,
            output={"planejamento": resposta},
        )

    async def _alocar_slot(self, scope: Scope, req: AgentRequest) -> AgentResponse:
        """Aloca um item a um slot específico."""
        return AgentResponse(
            request_id=req.request_id,
            ok=True,
            output={"alocado": True, "nota": "Stub — implementação completa na Fase 1"},
        )
