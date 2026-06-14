"""Migration 001 — Seed do tenant Victor + marcas éozoré e AINewz (idempotente).

Carrega brand profiles (doc 04), estratégias (doc 02), team_subscriptions (doc 09 §3)
e configuração do tenant (doc 05) no Firestore.

Uso: python -m migrations.001_seed_tenant_and_brands
"""

import asyncio

from google.cloud.firestore_v1 import AsyncClient

TENANT_ID = "victor"

TENANT_CONFIG = {
    "tenant_id": TENANT_ID,
    "platform_status": "ativo",
    "budget_mensal_brl": 600.0,
    "gasto_mes_ledger_brl": 0.0,
}

TEAM_SUBSCRIPTIONS = {
    "core": {"team_id": "core", "ativo": True, "obrigatorio": True},
    "linkedin": {"team_id": "linkedin", "ativo": True, "obrigatorio": False},
    "meta": {"team_id": "meta", "ativo": True, "obrigatorio": False},
    "blog": {"team_id": "blog", "ativo": True, "obrigatorio": False},
    "radar": {"team_id": "radar", "ativo": True, "obrigatorio": False},
    "comunidade": {"team_id": "comunidade", "ativo": True, "obrigatorio": False},
    "analytics_web": {"team_id": "analytics_web", "ativo": True, "obrigatorio": False},
    "youtube": {"team_id": "youtube", "ativo": False, "obrigatorio": False},
    "tiktok": {"team_id": "tiktok", "ativo": False, "obrigatorio": False},
    "email": {"team_id": "email", "ativo": False, "obrigatorio": False},
    "video_ia": {"team_id": "video_ia", "ativo": False, "obrigatorio": False},
}

BRAND_EOZORE = {
    "brand_id": "eozore",
    "nome": "éozoré",
    "missao": (
        "provar que dados e IA são aprendíveis por qualquer pessoa disciplinada, "
        "unindo técnica, estatística e visão de negócio"
    ),
    "idioma": "pt-BR",
    "modo": "sandbox",
    "nivel_de_franqueza": 0.9,
    "buffer_minimo_dias": 7,
    "estrategia_ativa": "strategies/eozore/versions/v1-2026Q2",
}

BRAND_AINEWZ = {
    "brand_id": "ainewz",
    "nome": "AINewz",
    "missao": (
        "ser a curadoria confiável de notícias de IA em português: "
        "rápida, factual e com leitura crítica do que importa"
    ),
    "idioma": "pt-BR",
    "modo": "sandbox",
    "nivel_de_franqueza": 0.9,
    "buffer_minimo_dias": 2,
    "estrategia_ativa": "strategies/ainewz/versions/v1-2026Q2",
}

STRATEGY_EOZORE = {
    "version": "v1-2026Q2",
    "status": "ativa",
    "objetivo": "construir autoridade e audiência em transição de carreira para dados/IA",
    "tese_central": (
        "qualquer profissional disciplinado consegue migrar para dados/IA "
        "com fundamentos sólidos e portfólio real"
    ),
    "objetivo_de_conversao": {
        "tipo": "audiencia",
        "metrica_primaria": "novos_seguidores + novos_inscritos_youtube",
    },
    "pilares": [
        {"nome": "fundamentos sem medo", "peso": 0.4},
        {"nome": "carreira e mercado", "peso": 0.3},
        {"nome": "ia aplicada a negócios", "peso": 0.2},
        {"nome": "bastidores e opinião", "peso": 0.1},
    ],
}

STRATEGY_AINEWZ = {
    "version": "v1-2026Q2",
    "status": "ativa",
    "objetivo": "crescer audiência recorrente do portal/newsletter usando redes como topo de funil",
    "objetivo_de_conversao": {
        "tipo": "audiencia",
        "metrica_primaria": "novos_assinantes_newsletter",
    },
    "pilares": [
        {"nome": "lançamentos e modelos", "peso": 0.35},
        {"nome": "ia + negócios no Brasil", "peso": 0.30},
        {"nome": "regulação e governança", "peso": 0.20},
        {"nome": "pesquisa explicada", "peso": 0.15},
    ],
}


async def run() -> None:
    db = AsyncClient()

    # Tenant config
    await db.document(f"tenant/{TENANT_ID}/config/main").set(TENANT_CONFIG, merge=True)
    print(f"✓ Tenant config: {TENANT_ID}")

    # Team subscriptions
    for team_id, data in TEAM_SUBSCRIPTIONS.items():
        await db.document(f"tenant/{TENANT_ID}/team_subscriptions/{team_id}").set(data, merge=True)
    print(f"✓ Team subscriptions: {len(TEAM_SUBSCRIPTIONS)} times")

    # Brand éozoré
    await db.document(f"tenant/{TENANT_ID}/brands/eozore").set(BRAND_EOZORE, merge=True)
    await db.document(f"tenant/{TENANT_ID}/brands/eozore/strategies/versions/v1-2026Q2").set(
        STRATEGY_EOZORE, merge=True
    )
    print("✓ Brand éozoré + estratégia v1-2026Q2")

    # Brand AINewz
    await db.document(f"tenant/{TENANT_ID}/brands/ainewz").set(BRAND_AINEWZ, merge=True)
    await db.document(f"tenant/{TENANT_ID}/brands/ainewz/strategies/versions/v1-2026Q2").set(
        STRATEGY_AINEWZ, merge=True
    )
    print("✓ Brand AINewz + estratégia v1-2026Q2")

    print("\n✅ Migration 001 completa (idempotente).")


if __name__ == "__main__":
    asyncio.run(run())
