"""Migration 001 — Seed de dados GLOBAIS da plataforma (idempotente).

APENAS dados de platform/ (global, compartilhado entre tenants):
- model_routing
- pricing
- config base

NÃO contém dados de nenhuma marca ou tenant específico.
Dados de tenant/marca são criados via cockpit (onboarding self-service).

Uso: python -m migrations.001_seed_platform_globals
"""

import asyncio

from google.cloud.firestore_v1 import AsyncClient

PLATFORM_MODEL_ROUTING = {
    "estrutural": "gemini-2.5-flash",
    "analitica": "gemini-2.5-pro",
    "criativa": "claude-opus-4-6",
    "conselho": "claude-opus-4-6",
    "embedding": "text-embedding-005",
    "economia": {
        "estrutural": "gemini-2.5-flash",
        "analitica": "gemini-2.5-flash",
        "criativa": "claude-sonnet-4-6",
        "conselho": "claude-sonnet-4-6",
        "embedding": "text-embedding-005",
    },
}

PLATFORM_PRICING = {
    "claude-opus-4-6": {"input_per_1m_usd": 15.0, "output_per_1m_usd": 75.0},
    "claude-sonnet-4-6": {"input_per_1m_usd": 3.0, "output_per_1m_usd": 15.0},
    "gemini-2.5-flash": {"input_per_1m_usd": 0.15, "output_per_1m_usd": 0.60},
    "gemini-2.5-pro": {"input_per_1m_usd": 1.25, "output_per_1m_usd": 10.0},
    "text-embedding-005": {"input_per_1m_usd": 0.025, "output_per_1m_usd": 0.0},
    "cambio_usd_brl": 5.25,
}


async def run() -> None:
    db = AsyncClient()

    # Model routing (doc 03 §1)
    await db.document("platform/model_routing/config/main").set(PLATFORM_MODEL_ROUTING, merge=True)
    print("✓ platform/model_routing")

    # Pricing (doc 05 §2)
    await db.document("platform/pricing/config/main").set(PLATFORM_PRICING, merge=True)
    print("✓ platform/pricing")

    print("\n✅ Migration 001 completa — apenas dados globais (platform/).")
    print("   Dados de tenant/marca são criados via cockpit (onboarding).")


if __name__ == "__main__":
    asyncio.run(run())
