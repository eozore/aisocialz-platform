"""Redator — texto nativo por canal (doc 03 §3).

Nunca "adapta" mecanicamente — reescreve para a gramática do canal.
Insere referências do grafo no formato como_referenciar.
Consulta o grafo SEMPRE antes de produzir (doc 02 regra 2).

Modelo: Claude no passe final
Time: core (obrigatório)
"""

from agents.base import PlatformAgent
from core_domain import AgentRequest, AgentResponse, TaskKind


class RedatorAgent(PlatformAgent):
    agent_id = "redator"
    team = "core"

    async def handle(self, req: AgentRequest) -> AgentResponse:
        """Produz texto nativo para o canal.

        Payload esperado:
        - pauta: str (briefing do que escrever)
        - canal: str
        - formato: str
        - referencias_grafo: list[dict] (nós relevantes do retrieval)
        """
        scope = req.scope
        pauta = str(req.payload.get("pauta", ""))
        canal = str(req.payload.get("canal", ""))
        formato = str(req.payload.get("formato", ""))
        referencias = req.payload.get("referencias_grafo", [])

        # Monta contexto com referências do grafo
        refs_text = ""
        if referencias:
            refs_text = "\n\nConteúdos anteriores relevantes (inserir referência acionável):\n"
            for ref in referencias:  # type: ignore[union-attr]
                if isinstance(ref, dict):
                    titulo_ref = ref.get("titulo", "")
                    como_ref = ref.get("como_referenciar", {}).get(canal, "")
                    refs_text += f"- {titulo_ref}: {como_ref}\n"

        messages = [
            {
                "role": "system",
                "content": (
                    f"Você é o Redator. Produza texto NATIVO para {canal} no formato {formato}. "
                    "Não adapte mecanicamente — reescreva para a gramática do canal. "
                    "LinkedIn ≠ thread ≠ legenda IG. "
                    "Se há conteúdo anterior relevante, INSIRA a referência acionável no "
                    "formato nativo do canal (link, menção ao canal, etc.). "
                    "Nunca diga 'já falei disso' sem dar caminho concreto de acesso."
                ),
            },
            {
                "role": "user",
                "content": f"Pauta: {pauta}{refs_text}",
            },
        ]

        texto = await self._call_llm(scope, TaskKind.CRIATIVA, messages, req.item_id)

        return AgentResponse(
            request_id=req.request_id,
            ok=True,
            output={"texto": texto, "canal": canal, "formato": formato},
        )
