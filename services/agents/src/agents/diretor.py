"""Diretor — orquestrador + conselheiro (doc 03 §3).

Missão dupla:
1. Transformar estratégia em execução e proteger as regras do sistema
2. Ser o conselheiro de marketing do CEO (interface em linguagem de negócio)

Modelo: Opus 4.6
Time: core (obrigatório, sempre ativo)
"""

from agents.base import PlatformAgent
from core_domain import AgentRequest, AgentResponse, Scope, TaskKind


class DiretorAgent(PlatformAgent):
    agent_id = "diretor"
    team = "core"

    async def handle(self, req: AgentRequest) -> AgentResponse:
        """Processa tarefas do Diretor.

        Tasks suportadas:
        - "conselho": responde consulta do CEO em linguagem de negócio
        - "distribuir_backlog": distribui slots do dia para produção
        - "consolidar_planejamento": consolida calendário semanal
        - "relatorio_semanal": gera relatório para o CEO
        """
        task = req.task
        scope = req.scope

        if task == "conselho":
            return await self._conselho(scope, req)
        elif task == "distribuir_backlog":
            return await self._distribuir(scope, req)
        else:
            return AgentResponse(
                request_id=req.request_id,
                ok=False,
                output={"erro": f"Task '{task}' não implementada no Diretor"},
            )

    async def _conselho(self, scope: Scope, req: AgentRequest) -> AgentResponse:
        """Conversa com o CEO em linguagem de negócio (doc 03 §3, doc 09 §1)."""
        mensagem_ceo = str(req.payload.get("mensagem", ""))

        messages = [
            {
                "role": "system",
                "content": (
                    "Você é o Diretor de Marketing (CMO de IA) desta marca. "
                    "Converse em linguagem de negócio. Recomende com candor. "
                    "Discorde quando o pedido fere a estratégia ativa. "
                    "Nunca abra com elogio. Use o formato: POSIÇÃO + EVIDÊNCIA + "
                    "CONTRA-ARGUMENTO + CONFIANÇA."
                ),
            },
            {"role": "user", "content": mensagem_ceo},
        ]

        resposta = await self._call_llm(scope, TaskKind.CONSELHO, messages)

        return AgentResponse(
            request_id=req.request_id,
            ok=True,
            output={"resposta": resposta},
        )

    async def _distribuir(self, scope: Scope, req: AgentRequest) -> AgentResponse:
        """Distribui slots do dia para agentes de produção."""
        # Stub: na implementação completa, lê schedule do dia e cria AgentRequests
        return AgentResponse(
            request_id=req.request_id,
            ok=True,
            output={"distribuidos": 0, "nota": "Implementação completa na Fase 1"},
        )
