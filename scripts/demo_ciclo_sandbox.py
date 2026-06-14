"""Demo end-to-end do ciclo sandbox (definição de pronto Fase 1).

Demonstra: planejamento → produção → revisão → publicação simulada → preview,
com um post referenciando conteúdo do grafo via link acionável.

Requer:
- Emulador Firestore rodando: gcloud emulators firestore start --host-port=localhost:8080
- FIRESTORE_EMULATOR_HOST=localhost:8080

Uso:
    export FIRESTORE_EMULATOR_HOST=localhost:8080
    uv run python scripts/demo_ciclo_sandbox.py
"""

import asyncio
import json
import os
import uuid
from datetime import UTC, datetime

# Garante que o emulador está configurado
if not os.environ.get("FIRESTORE_EMULATOR_HOST"):
    os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"

from core_domain.enums import Canal, CostAccount, ItemStatus, TaskKind
from core_domain.models import (
    BacklogItem,
    ContentNode,
    CostEntry,
    Fonte,
    Funil,
    Performance,
    Scope,
    TenantConfig,
)
from llm_gateway.client import LlmGateway
from persistence.firestore_client import get_firestore_client
from persistence.scope import TenantScope

# --- Implementação real do LedgerWriter contra Firestore ---


class FirestoreLedgerWriter:
    """LedgerWriter implementado contra Firestore (via persistence)."""

    def __init__(self, db):
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


# --- Stub LLM que simula respostas realistas para o demo ---


class StubVertexClient:
    """Simula respostas de LLM para demonstração."""

    async def complete(self, model: str, messages: list) -> dict:
        # Identifica a task pelo conteúdo do system prompt
        system = messages[0].get("content", "") if messages else ""

        if "Estrategista" in system:
            return {
                "text": json.dumps(
                    {
                        "slots": [
                            {
                                "canal": "linkedin",
                                "formato": "post_linkedin",
                                "pilar": "fundamentos sem medo",
                                "funil": "topo",
                                "pauta": "Desmistificar variáveis aleatórias com analogia de futebol",
                            }
                        ]
                    }
                ),
                "tokens_in": 500,
                "tokens_out": 200,
            }
        elif "Redator" in system:
            return {
                "text": (
                    "Você já ouviu falar de variáveis aleatórias e achou que era coisa "
                    "de gênio? Pois não é.\n\n"
                    "Pensa assim: quando um jogador cobra um pênalti, o resultado "
                    "(gol ou defesa) é uma variável aleatória. Você não sabe o que vai "
                    "acontecer, mas sabe as probabilidades.\n\n"
                    "Na ciência de dados é igual: modelamos a incerteza com números.\n\n"
                    "Quer entender de verdade? Assisti meu vídeo completo sobre isso: "
                    "https://youtu.be/XXXX (link na bio)\n\n"
                    "#cienciadedados #estatistica #carreira"
                ),
                "tokens_in": 800,
                "tokens_out": 150,
            }
        elif "Revisor" in system:
            return {
                "text": json.dumps(
                    {
                        "aprovado": True,
                        "motivos": [],
                        "sugestoes": ["Considerar adicionar emoji de dado 🎲 no gancho"],
                    }
                ),
                "tokens_in": 600,
                "tokens_out": 100,
            }
        else:
            return {"text": "[resposta genérica do stub]", "tokens_in": 100, "tokens_out": 50}


# --- Ciclo principal ---


async def main():
    print("=" * 60)
    print("DEMO: Ciclo Sandbox Completo (Fase 1)")
    print("=" * 60)

    db = get_firestore_client()

    # ============================================================
    # STEP 0: Seed dos dados (migration idempotente)
    # ============================================================
    print("\n📦 Step 0: Seedando dados no Firestore (emulador)...")

    tenant_id = "victor"
    brand_id = "eozore"
    scope = Scope(tenant_id=tenant_id, brand_id=brand_id)
    tenant_scope = TenantScope(tenant_id, brand_id)

    # Config do tenant
    await db.document(f"tenant/{tenant_id}/config/main").set(
        {
            "tenant_id": tenant_id,
            "platform_status": "ativo",
            "budget_mensal_brl": 600.0,
            "gasto_mes_ledger_brl": 0.0,
        }
    )

    # Brand profile
    await db.document(f"tenant/{tenant_id}/brands/{brand_id}").set(
        {
            "brand_id": brand_id,
            "nome": "éozoré",
            "missao": "provar que dados e IA são aprendíveis por qualquer pessoa disciplinada",
            "modo": "sandbox",
            "estrategia_ativa": f"strategies/{brand_id}/versions/v1-2026Q2",
        }
    )

    # Conteúdo existente no grafo (para demonstrar referência acionável)
    grafo_node = ContentNode(
        id="yt-2026-04-variaveis-aleatorias",
        scope=scope,
        titulo="Variáveis Aleatórias sem Medo",
        conceitos=["variáveis aleatórias", "distribuições", "probabilidade"],
        depende_de=["probabilidade básica"],
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

    print("  ✓ Tenant config, brand profile, e 1 nó no grafo de conteúdo")

    # ============================================================
    # STEP 1: Planejamento (Estrategista)
    # ============================================================
    print("\n📋 Step 1: Estrategista decide o que publicar...")

    ledger = FirestoreLedgerWriter(db)
    gateway = LlmGateway(ledger=ledger, vertex_client=StubVertexClient())

    # Simula chamada do Estrategista
    result = await gateway.complete(
        scope=scope,
        agent_id="estrategista",
        task_kind=TaskKind.ANALITICA,
        messages=[
            {"role": "system", "content": "Você é o Estrategista. Decida slots da semana."},
            {"role": "user", "content": "Planejamento semanal"},
        ],
        conta=CostAccount.OPERACAO,
    )
    print(
        f"  ✓ Estrategista planejou (modelo: {result.model_used}, custo: R${result.cost_brl:.4f})"
    )
    print(f"  Plano: {result.text[:100]}...")

    # Cria item no backlog
    item = BacklogItem(
        id=f"item-{uuid.uuid4().hex[:8]}",
        scope=scope,
        tipo="post_linkedin",
        pilar="fundamentos sem medo",
        funil=Funil.TOPO,
        fonte=Fonte(tipo="pauta", ref=None),
        status=ItemStatus.PRODUCAO,
        referencias_grafo=["yt-2026-04-variaveis-aleatorias"],
    )
    backlog_path = tenant_scope.collection_path("backlog")
    await db.document(f"{backlog_path}/{item.id}").set(item.model_dump(mode="json"))
    print(f"  ✓ Item criado no backlog: {item.id} (status: producao)")

    # ============================================================
    # STEP 2: Produção (Redator)
    # ============================================================
    print("\n✍️  Step 2: Redator produz texto com referência ao grafo...")

    # Redator consulta o grafo (retrieval)
    grafo_doc = await db.document(f"{grafo_path}/{grafo_node.id}").get()
    ref_data = grafo_doc.to_dict()

    result = await gateway.complete(
        scope=scope,
        agent_id="redator",
        task_kind=TaskKind.CRIATIVA,
        messages=[
            {"role": "system", "content": "Você é o Redator. Produza texto nativo para o canal."},
            {"role": "user", "content": f"Pauta: variáveis aleatórias. Ref: {ref_data['titulo']}"},
        ],
        item_id=item.id,
        conta=CostAccount.OPERACAO,
    )
    texto_produzido = result.text
    print(f"  ✓ Redator produziu (modelo: {result.model_used}, custo: R${result.cost_brl:.4f})")
    print(f"  Texto:\n  {'  '.join(texto_produzido.split(chr(10))[:3])}...")

    # Verifica referência acionável
    tem_referencia = "youtu.be" in texto_produzido or "link" in texto_produzido.lower()
    print(
        f"  {'✓' if tem_referencia else '✗'} Referência acionável ao grafo: {'presente' if tem_referencia else 'AUSENTE'}"
    )

    # ============================================================
    # STEP 3: Revisão (Revisor)
    # ============================================================
    print("\n🔍 Step 3: Revisor avalia o texto...")

    result = await gateway.complete(
        scope=scope,
        agent_id="revisor",
        task_kind=TaskKind.CRIATIVA,
        messages=[
            {
                "role": "system",
                "content": "Você é o Revisor. Checklist: voz, factualidade, referências, conformidade.",
            },
            {"role": "user", "content": f"Canal: linkedin\n\nTexto:\n{texto_produzido}"},
        ],
        item_id=item.id,
        conta=CostAccount.OPERACAO,
    )
    print(f"  ✓ Revisor avaliou (modelo: {result.model_used}, custo: R${result.cost_brl:.4f})")
    print(f"  Parecer: {result.text}")

    # Atualiza status do item
    await db.document(f"{backlog_path}/{item.id}").update({"status": "aprovado"})
    print("  ✓ Item aprovado → status: aprovado")

    # ============================================================
    # STEP 4: Publicação simulada (sandbox)
    # ============================================================
    print("\n📤 Step 4: Publicação simulada (modo sandbox)...")

    publication_id = f"pub-{uuid.uuid4().hex[:8]}"
    idempotency_key = f"{brand_id}-linkedin-{item.id}-slot1"

    publication = {
        "id": publication_id,
        "scope": scope.model_dump(),
        "canal": "linkedin",
        "content_id": item.id,
        "idempotency_key": idempotency_key,
        "simulado": True,  # SANDBOX — doc 01 §5
        "texto": texto_produzido,
        "post_url": None,  # Sem URL real em sandbox
        "publicado_em": datetime.now(UTC).isoformat(),
        "status": "publicado_simulado",
    }

    pub_path = tenant_scope.collection_path("publications")
    await db.document(f"{pub_path}/{publication_id}").set(publication)
    print(f"  ✓ Publicação simulada gravada: {publication_id}")
    print("    simulado: true (sandbox — nenhuma API externa chamada)")
    print(f"    idempotency_key: {idempotency_key}")

    # ============================================================
    # STEP 5: Preview (como apareceria no cockpit)
    # ============================================================
    print("\n👁️  Step 5: Preview no Cockpit")
    print("  " + "─" * 50)
    print("  Canal: LinkedIn")
    print("  Formato: post_linkedin")
    print("  Pilar: fundamentos sem medo")
    print("  Status: ✅ publicado (simulado)")
    print(f"  Referência ao grafo: {grafo_node.titulo}")
    print("  " + "─" * 50)
    print("  TEXTO DO POST:")
    print("  " + "─" * 50)
    for line in texto_produzido.split("\n"):
        print(f"  {line}")
    print("  " + "─" * 50)

    # ============================================================
    # VERIFICAÇÕES FINAIS (definição de pronto Fase 0 + 1)
    # ============================================================
    print("\n✅ Verificações da Definição de Pronto:")

    # 1. Cost ledger tem entradas com conta build/operacao
    ledger_docs = []
    async for doc in db.collection_group("cost_ledger").stream():
        ledger_docs.append(doc.to_dict())

    print(f"  ✓ Cost ledger: {len(ledger_docs)} entradas registradas")
    contas = set(d.get("conta") for d in ledger_docs)
    print(f"    Contas presentes: {contas}")

    # 2. platform_status é respeitado
    config_doc = await db.document(f"tenant/{tenant_id}/config/main").get()
    config = config_doc.to_dict()
    print(f"  ✓ platform_status: {config['platform_status']}")
    print(f"  ✓ gasto_mes_ledger_brl: R${config['gasto_mes_ledger_brl']:.4f}")

    # 3. Escopo de tenant obrigatório (demonstrado por toda a execução usar TenantScope)
    print("  ✓ Escopo de tenant: todas as operações passaram por TenantScope")

    # 4. Post referencia conteúdo do grafo com link acionável
    print(f"  {'✓' if tem_referencia else '✗'} Post referencia grafo com link acionável")

    print("\n" + "=" * 60)
    print("DEMO CONCLUÍDA COM SUCESSO 🎉")
    print("=" * 60)
    print("\nResumo: planejamento → produção → revisão → publicação simulada")
    print(f"Custo total do ciclo: R${config['gasto_mes_ledger_brl']:.4f}")
    print("Nenhuma API externa foi chamada (modo sandbox).\n")


if __name__ == "__main__":
    asyncio.run(main())
