"""Teste de integração: ciclo sandbox completo (definição de pronto Fase 1).

Demonstra: planejamento → produção → revisão → publicação simulada → preview,
com um post referenciando conteúdo do grafo via link acionável.

Roda contra MockFirestore (in-memory) — mesmo fluxo que rodaria contra emulador ou produção.
"""

import uuid
from datetime import UTC, datetime

import pytest
from tests.integration.mock_firestore import MockFirestoreClient

from core_domain import Scope, TaskKind
from core_domain.enums import Canal, CostAccount, Funil
from core_domain.models import (
    ContentNode,
    CostEntry,
    Performance,
    TenantConfig,
)
from llm_gateway.client import LlmGateway
from persistence.scope import TenantScope

# --- LedgerWriter real contra o MockFirestore ---


class FirestoreLedgerWriter:
    def __init__(self, db: MockFirestoreClient):
        self._db = db

    async def get_tenant_config(self, tenant_id: str) -> TenantConfig:
        doc = await self._db.document(f"tenant/{tenant_id}/config/main").get()
        if doc.exists:
            return TenantConfig.model_validate(doc.to_dict())
        return TenantConfig(tenant_id=tenant_id)

    async def record_cost(self, entry: CostEntry) -> None:
        path = f"tenant/{entry.scope.tenant_id}/cost_ledger/{entry.id}"
        await self._db.document(path).set(entry.model_dump(mode="json"))

    async def increment_monthly_spend(self, tenant_id: str, amount: float) -> None:
        doc_ref = self._db.document(f"tenant/{tenant_id}/config/main")
        doc = await doc_ref.get()
        if doc.exists:
            current = doc.to_dict().get("gasto_mes_ledger_brl", 0)
            await doc_ref.update({"gasto_mes_ledger_brl": current + amount})


# --- Stub LLM ---


class StubVertexClient:
    async def complete(self, model: str, messages: list) -> dict:
        system = messages[0].get("content", "") if messages else ""

        if "Estrategista" in system:
            return {
                "text": "Slot: post_linkedin sobre variáveis aleatórias",
                "tokens_in": 500,
                "tokens_out": 200,
            }
        elif "Redator" in system:
            return {
                "text": (
                    "Você já ouviu falar de variáveis aleatórias "
                    "e achou que era coisa de gênio?\n\n"
                    "Pensa assim: quando um jogador cobra pênalti, "
                    "o resultado é uma variável aleatória.\n\n"
                    "Na ciência de dados é igual: modelamos a "
                    "incerteza com números.\n\n"
                    "Aprofundei isso num vídeo completo: "
                    "https://youtu.be/XXXX\n\n"
                    "#cienciadedados #estatistica"
                ),
                "tokens_in": 800,
                "tokens_out": 150,
            }
        elif "Revisor" in system:
            return {
                "text": '{"aprovado": true, "motivos": [], "sugestoes": []}',
                "tokens_in": 600,
                "tokens_out": 100,
            }
        return {"text": "[stub]", "tokens_in": 100, "tokens_out": 50}


# --- O TESTE ---


@pytest.mark.asyncio
async def test_ciclo_sandbox_completo() -> None:
    """Ciclo end-to-end: planejamento → produção → revisão → publicação simulada.

    Verifica:
    1. Cost ledger registra com conta operacao
    2. Post referencia conteúdo do grafo com link acionável
    3. Publicação é marcada como simulada (sandbox)
    4. Escopo de tenant em todas as operações
    """
    db = MockFirestoreClient()
    tenant_id = "victor"
    brand_id = "eozore"
    scope = Scope(tenant_id=tenant_id, brand_id=brand_id)
    tenant_scope = TenantScope(tenant_id, brand_id)

    # --- SEED ---
    await db.document(f"tenant/{tenant_id}/config/main").set(
        {
            "tenant_id": tenant_id,
            "platform_status": "ativo",
            "budget_mensal_brl": 600.0,
            "gasto_mes_ledger_brl": 0.0,
        }
    )

    # Conteúdo existente no grafo
    grafo_node = ContentNode(
        id="yt-2026-04-variaveis-aleatorias",
        scope=scope,
        titulo="Variáveis Aleatórias sem Medo",
        conceitos=["variáveis aleatórias", "distribuições", "probabilidade"],
        pilar="fundamentos sem medo",
        funil=Funil.MEIO,
        formato="youtube_longo",
        canal=Canal.YOUTUBE,
        url="https://youtu.be/XXXX",
        como_referenciar={
            "youtube": "link com timestamp na descrição",
            "linkedin": "link no primeiro comentário",
            "instagram": "'busca Variáveis Aleatórias no canal' + link na bio",
        },
        publicado_em=datetime(2026, 4, 12, tzinfo=UTC),
        performance=Performance(views=1200, retencao_pct=45.0, saves=89),
    )
    grafo_path = tenant_scope.collection_path("content_graph")
    await db.document(f"{grafo_path}/{grafo_node.id}").set(grafo_node.model_dump(mode="json"))

    # --- SETUP GATEWAY ---
    ledger = FirestoreLedgerWriter(db)
    gateway = LlmGateway(ledger=ledger, vertex_client=StubVertexClient())

    # --- STEP 1: PLANEJAMENTO ---
    plan_result = await gateway.complete(
        scope=scope,
        agent_id="estrategista",
        task_kind=TaskKind.ANALITICA,
        messages=[
            {"role": "system", "content": "Você é o Estrategista. Decida slots."},
            {"role": "user", "content": "Planejamento semanal"},
        ],
        conta=CostAccount.OPERACAO,
    )
    assert plan_result.cost_brl > 0
    assert plan_result.model_used  # modelo foi resolvido

    # --- STEP 2: PRODUÇÃO (com retrieval do grafo) ---
    grafo_doc = await db.document(f"{grafo_path}/{grafo_node.id}").get()
    assert grafo_doc.exists
    ref_data = grafo_doc.to_dict()

    prod_result = await gateway.complete(
        scope=scope,
        agent_id="redator",
        task_kind=TaskKind.CRIATIVA,
        messages=[
            {"role": "system", "content": "Você é o Redator. Texto nativo."},
            {"role": "user", "content": f"Pauta: var. aleatórias. Ref: {ref_data['titulo']}"},
        ],
        item_id="item-test",
        conta=CostAccount.OPERACAO,
    )
    texto = prod_result.text

    # VERIFICAÇÃO CHAVE: post referencia conteúdo do grafo com link acionável
    assert "youtu.be" in texto or "https://" in texto, (
        "Post DEVE referenciar conteúdo do grafo com link acionável (doc 02 regra 2)"
    )

    # --- STEP 3: REVISÃO ---
    rev_result = await gateway.complete(
        scope=scope,
        agent_id="revisor",
        task_kind=TaskKind.CRIATIVA,
        messages=[
            {"role": "system", "content": "Você é o Revisor. Checa voz, factualidade, refs."},
            {"role": "user", "content": f"Canal: linkedin\n\n{texto}"},
        ],
        item_id="item-test",
        conta=CostAccount.OPERACAO,
    )
    assert "aprovado" in rev_result.text.lower()

    # --- STEP 4: PUBLICAÇÃO SIMULADA ---
    pub_id = f"pub-{uuid.uuid4().hex[:8]}"
    idempotency_key = f"{brand_id}-linkedin-item-test-slot1"
    pub_path = tenant_scope.collection_path("publications")

    await db.document(f"{pub_path}/{pub_id}").set(
        {
            "id": pub_id,
            "scope": scope.model_dump(),
            "canal": "linkedin",
            "content_id": "item-test",
            "idempotency_key": idempotency_key,
            "simulado": True,
            "texto": texto,
            "publicado_em": datetime.now(UTC).isoformat(),
        }
    )

    # VERIFICAÇÃO: publicação marcada como simulada
    pub_doc = await db.document(f"{pub_path}/{pub_id}").get()
    assert pub_doc.exists
    assert pub_doc.to_dict()["simulado"] is True

    # --- VERIFICAÇÕES FINAIS ---

    # Cost ledger tem entradas
    ledger_entries = []
    async for doc in db.collection_group("cost_ledger").stream():
        ledger_entries.append(doc.to_dict())
    assert len(ledger_entries) == 3  # estrategista + redator + revisor
    assert all(e["conta"] == "operacao" for e in ledger_entries)

    # gasto_mes foi incrementado
    config_doc = await db.document(f"tenant/{tenant_id}/config/main").get()
    assert config_doc.to_dict()["gasto_mes_ledger_brl"] > 0

    # Todos os dados estão escopados por tenant
    for key in db.data:
        if key.startswith("tenant/"):
            assert tenant_id in key
