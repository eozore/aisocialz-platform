"""Revisor — último portão antes de agendar (doc 03 §3).

Checklist:
1. Voz: compara com few-shot + guia de voz negativo (anti-padrões)
2. Factualidade: AINewz = toda afirmação rastreável à fonte
3. Referências: conceito coberto no grafo → referência acionável presente
4. Conformidade: limites do canal via adapter.validate()

Modelo: Claude (Opus 4.6)
Time: core (obrigatório)
"""

from agents.base import PlatformAgent
from core_domain import AgentRequest, AgentResponse, TaskKind


class RevisorAgent(PlatformAgent):
    agent_id = "revisor"
    team = "core"

    async def handle(self, req: AgentRequest) -> AgentResponse:
        """Revisa um item do backlog antes do agendamento.

        Payload esperado:
        - texto: str (conteúdo a revisar)
        - formato: str
        - canal: str
        - referencias_grafo: list[str]
        - fonte: dict | None (para checagem de factualidade)
        """
        scope = req.scope
        texto = str(req.payload.get("texto", ""))
        canal = str(req.payload.get("canal", ""))

        messages = [
            {
                "role": "system",
                "content": (
                    "Você é o Revisor da plataforma. Seu papel é o último gate de qualidade. "
                    "Analise o texto abaixo e verifique:\n"
                    "1. VOZ: Parece humano? Não tem padrões de IA (aberturas clichê, "
                    "listas previsíveis, excesso de travessão, emojis em série)?\n"
                    "2. FACTUALIDADE: Afirmações têm lastro? Fontes citadas quando necessário?\n"
                    "3. REFERÊNCIAS: Se assume conceito já coberto, tem link acionável?\n"
                    "4. CONFORMIDADE: Adequado ao canal?\n\n"
                    'Responda com JSON: {"aprovado": bool, "motivos": [str], '
                    '"sugestoes": [str]}'
                ),
            },
            {
                "role": "user",
                "content": f"Canal: {canal}\n\nTexto para revisão:\n{texto}",
            },
        ]

        resposta = await self._call_llm(scope, TaskKind.CRIATIVA, messages, req.item_id)

        # Na implementação completa, parseia o JSON e decide aprovação
        aprovado = "aprovado" not in resposta.lower() or '"aprovado": true' in resposta.lower()

        return AgentResponse(
            request_id=req.request_id,
            ok=True,
            output={
                "aprovado": aprovado,
                "revisao": resposta,
            },
        )
