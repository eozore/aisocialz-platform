"""Radar / Contexto — momentos relevantes do mundo (doc 03 §3).

Traz ao Estrategista eventos que um bom marqueteiro consideraria.
Regra de ouro: força da ponte — conexão GENUÍNA com pilar da marca.
Gancho forçado é proibido.

Modelo: Flash (coleta) + Pro/Sonnet (pontuação de ponte)
Time: radar
"""

from agents.base import PlatformAgent
from core_domain import AgentRequest, AgentResponse, TaskKind


class RadarAgent(PlatformAgent):
    agent_id = "radar"
    team = "radar"

    async def handle(self, req: AgentRequest) -> AgentResponse:
        """Identifica momentos relevantes e pontua força da ponte.

        Tasks:
        - "varrer_momentos": busca eventos e pontua por marca
        """
        scope = req.scope

        messages = [
            {
                "role": "system",
                "content": (
                    "Você é o Radar. Identifique eventos/momentos relevantes que um "
                    "bom marqueteiro consideraria. Pontue cada um pela FORÇA DA PONTE "
                    "(0-1) com os pilares da marca. Gancho forçado é proibido. "
                    "Pode recomendar explicitamente IGNORAR um evento. "
                    "Retorne JSON: [{evento, tipo, forca_da_ponte, pilar_conectado, recomendacao}]"
                ),
            },
            {
                "role": "user",
                "content": "Quais momentos são relevantes para esta marca esta semana?",
            },
        ]

        resposta = await self._call_llm(scope, TaskKind.ANALITICA, messages)

        return AgentResponse(
            request_id=req.request_id,
            ok=True,
            output={"momentos": resposta},
        )
