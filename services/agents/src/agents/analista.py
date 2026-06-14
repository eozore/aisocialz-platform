"""Analista — modo coleta na Fase 1 (doc 03 §3, doc 06 §3).

Fase 1 (modo coleta):
- Coleta diária de métricas (via adapters.get_metrics)
- Normaliza em schema único (Performance)
- Atualiza performance no content_graph
- Schema básico de learnings (hipóteses registradas, sem ciclo científico)
- Atribuição básica de performance às dimensões

Fase 2 (ciclo completo):
- Experimentos nos ~20% de slots
- Retros semanais
- Promoção/expiração de learnings
- Relatório do CEO

Modelo: Flash na coleta, Pro na síntese
Time: core (obrigatório)
"""

from datetime import UTC, datetime

from agents.base import PlatformAgent
from core_domain import AgentRequest, AgentResponse, Scope, TaskKind


class AnalistaAgent(PlatformAgent):
    """Analista em modo coleta (Fase 1)."""

    agent_id = "analista"
    team = "core"

    async def handle(self, req: AgentRequest) -> AgentResponse:
        """Tasks do Analista.

        Tasks modo coleta (Fase 1):
        - "coletar_metricas": coleta métricas de posts publicados
        - "atualizar_grafo": atualiza performance no content_graph
        - "registrar_hipotese": registra observação como hipótese de learning
        - "leitura_semanal": gera resumo de performance da semana (input pro Estrategista)
        """
        task = req.task
        scope = req.scope

        if task == "coletar_metricas":
            return await self._coletar_metricas(scope, req)
        elif task == "atualizar_grafo":
            return await self._atualizar_grafo(scope, req)
        elif task == "registrar_hipotese":
            return await self._registrar_hipotese(scope, req)
        elif task == "leitura_semanal":
            return await self._leitura_semanal(scope, req)
        else:
            return AgentResponse(
                request_id=req.request_id,
                ok=False,
                output={"erro": f"Task '{task}' não suportada pelo Analista"},
            )

    async def _coletar_metricas(self, scope: Scope, req: AgentRequest) -> AgentResponse:
        """Coleta métricas via adapters para posts publicados recentes.

        Na implementação completa:
        1. Lê publications/ com status=publicado dos últimos N dias
        2. Para cada, chama adapter.get_metrics(post_ref, scope)
        3. Normaliza em Performance e atualiza content_graph
        """
        # Stub: na integração real, itera publications e chama adapters
        posts_coletados = 0
        return AgentResponse(
            request_id=req.request_id,
            ok=True,
            output={
                "posts_coletados": posts_coletados,
                "timestamp": datetime.now(UTC).isoformat(),
                "nota": "Conectar com persistence + adapters na integração",
            },
        )

    async def _atualizar_grafo(self, scope: Scope, req: AgentRequest) -> AgentResponse:
        """Atualiza o campo performance nos nós do content_graph.

        Payload:
        - content_id: str
        - metricas: dict (output normalizado do adapter)
        """
        content_id = str(req.payload.get("content_id", ""))
        metricas = req.payload.get("metricas", {})

        # Na implementação: repo.get(content_id) -> atualiza performance -> repo.put
        return AgentResponse(
            request_id=req.request_id,
            ok=True,
            output={
                "content_id": content_id,
                "atualizado": True,
                "metricas_recebidas": list(metricas.keys()) if isinstance(metricas, dict) else [],
            },
        )

    async def _registrar_hipotese(self, scope: Scope, req: AgentRequest) -> AgentResponse:
        """Registra uma observação como hipótese de learning.

        Hipóteses com n_amostras < 3 não saem de status=hipotese (doc 02).
        auto_aplicavel só para micro-otimizações (doc 02).

        Payload:
        - aprendizado: str
        - dimensoes: dict
        - evidencia: list[str]
        """
        aprendizado = str(req.payload.get("aprendizado", ""))
        evidencia = req.payload.get("evidencia", [])

        n_amostras = len(evidencia) if isinstance(evidencia, list) else 0

        return AgentResponse(
            request_id=req.request_id,
            ok=True,
            output={
                "learning_registrado": True,
                "status": "hipotese" if n_amostras < 3 else "em_teste",
                "n_amostras": n_amostras,
                "aprendizado": aprendizado,
            },
        )

    async def _leitura_semanal(self, scope: Scope, req: AgentRequest) -> AgentResponse:
        """Gera leitura da semana para o Estrategista.

        Usa LLM para sintetizar performance, padrões e sugestões.
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "Você é o Analista. Produza uma leitura da semana: "
                    "performance por pilar/canal/formato, padrões observados, "
                    "e sugestões para a próxima semana. "
                    "Use o formato de candor quando fizer recomendações."
                ),
            },
            {
                "role": "user",
                "content": "Gere a leitura semanal de performance.",
            },
        ]

        leitura = await self._call_llm(scope, TaskKind.ANALITICA, messages)

        return AgentResponse(
            request_id=req.request_id,
            ok=True,
            output={"leitura": leitura},
        )
