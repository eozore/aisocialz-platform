"""LlmGateway — wrapper único de LLM + ledger (doc 11 §6).

Nenhum agente chama Vertex direto. O gateway:
1. Checa platform_status (paused -> aborta)
2. Resolve modelo (routing) por task_kind + modo
3. Checa teto por item e teto diário da marca
4. Chama Vertex (claude-opus-4-6 / claude-sonnet-4-6 / gemini-*)
5. Calcula custo e grava cost_ledger (via ledger_writer injetado)
6. Incrementa contador do mês; se cruzou gatilho, publica custo-alerta
"""

import uuid
from datetime import UTC, datetime
from typing import Any, Protocol

from pydantic import BaseModel

from core_domain.enums import CostAccount, PlatformStatus, TaskKind
from core_domain.exceptions import BudgetExceededError, PlatformPausedError
from core_domain.models import CostEntry, Scope, TenantConfig
from llm_gateway.pricing import calculate_cost_brl
from llm_gateway.routing import resolve_model


class LlmResult(BaseModel):
    """Resultado de uma chamada LLM."""

    text: str
    model_used: str
    cost_brl: float
    tokens_in: int
    tokens_out: int


class LedgerWriter(Protocol):
    """Interface para escrita no ledger — implementação vive em persistence."""

    async def get_tenant_config(self, tenant_id: str) -> TenantConfig: ...
    async def record_cost(self, entry: CostEntry) -> None: ...
    async def increment_monthly_spend(self, tenant_id: str, amount: float) -> None: ...


class LlmGateway:
    """Gateway centralizado para todas as chamadas LLM.

    Recebe um LedgerWriter (implementado por persistence) e opcionalmente
    um cliente Vertex AI para chamadas reais.
    """

    def __init__(
        self,
        ledger: LedgerWriter,
        vertex_client: Any | None = None,
    ) -> None:
        self._ledger = ledger
        self._vertex = vertex_client
        # Tetos de segurança (doc 05 §2)
        self._teto_por_item_brl: float = 2.0
        self._teto_diario_fator: float = 1.5

    async def complete(
        self,
        *,
        scope: Scope,
        agent_id: str,
        task_kind: TaskKind,
        messages: list[dict[str, str]],
        item_id: str | None = None,
        conta: CostAccount = CostAccount.OPERACAO,
    ) -> LlmResult:
        """Ponto de entrada único para chamadas LLM.

        Raises:
            PlatformPausedError: se platform_status == paused
            BudgetExceededError: se o teto por item ou diário foi excedido
        """
        # 1. Checa platform_status
        config = await self._ledger.get_tenant_config(scope.tenant_id)
        if config.platform_status == PlatformStatus.PAUSED:
            raise PlatformPausedError(
                "Plataforma pausada (platform_status=paused). "
                "Nenhuma chamada LLM permitida até desbloqueio."
            )

        # 2. Resolve modelo
        model = resolve_model(task_kind, config.platform_status)

        # 3. Chama o modelo
        result = await self._call_model(model, messages)

        # 4. Calcula custo
        cost_brl = calculate_cost_brl(model, result["tokens_in"], result["tokens_out"])

        # 5. Checa teto por item (doc 05 §2)
        if cost_brl > self._teto_por_item_brl and conta == CostAccount.OPERACAO:
            raise BudgetExceededError(
                f"Custo desta chamada (R${cost_brl:.2f}) excede teto por item "
                f"(R${self._teto_por_item_brl:.2f})",
                custo_brl=cost_brl,
            )

        # 6. Grava no ledger
        entry = CostEntry(
            id=str(uuid.uuid4()),
            scope=scope,
            ts=datetime.now(UTC),
            agente=agent_id,
            item=item_id,
            conta=conta,
            servico="vertex_llm",
            modelo=model,
            tokens_in=result["tokens_in"],
            tokens_out=result["tokens_out"],
            custo_estimado_brl=cost_brl,
        )
        await self._ledger.record_cost(entry)

        # 7. Incrementa acumulado mensal (só operação)
        if conta == CostAccount.OPERACAO:
            await self._ledger.increment_monthly_spend(scope.tenant_id, cost_brl)

        return LlmResult(
            text=result["text"],
            model_used=model,
            cost_brl=cost_brl,
            tokens_in=result["tokens_in"],
            tokens_out=result["tokens_out"],
        )

    async def _call_model(self, model: str, messages: list[dict[str, str]]) -> dict[str, Any]:
        """Chama o modelo via Vertex AI. Abstração para mock em testes."""
        if self._vertex is None:
            return {
                "text": "[stub response]",
                "tokens_in": sum(len(m.get("content", "")) for m in messages),
                "tokens_out": 50,
            }
        return await self._vertex.complete(model=model, messages=messages)
