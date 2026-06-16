"""Cliente real do Vertex AI (Claude via Anthropic Vertex SDK).

Usado pelo LlmGateway quando vertex_client não é None.
Região: global | Modelo: claude-sonnet-4-5@20250929
"""

from anthropic import AnthropicVertex


class VertexAIClient:
    """Wrapper para chamadas ao Claude via Vertex AI."""

    def __init__(self, project_id: str, region: str = "global") -> None:
        self._client = AnthropicVertex(project_id=project_id, region=region)

    async def complete(self, model: str, messages: list[dict[str, str]]) -> dict:
        """Chama o modelo e retorna texto + contagem de tokens."""
        # Separa system message das user/assistant messages
        system_content = ""
        chat_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                system_content = msg.get("content", "")
            else:
                chat_messages.append(msg)

        # Se não há mensagens de chat, usa a system como user
        if not chat_messages:
            chat_messages = [{"role": "user", "content": system_content}]
            system_content = ""

        # Chamada síncrona (Anthropic SDK)
        kwargs: dict = {
            "model": model,
            "max_tokens": 2048,
            "messages": chat_messages,
        }
        if system_content:
            kwargs["system"] = system_content

        response = self._client.messages.create(**kwargs)

        text = response.content[0].text if response.content else ""
        tokens_in = response.usage.input_tokens
        tokens_out = response.usage.output_tokens

        return {
            "text": text,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
        }
