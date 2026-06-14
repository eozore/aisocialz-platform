"""Migration 002 — Seed do catálogo de formatos (doc 10 §2) + templates base.

Popula platform/format_catalog com os formatos da V1.
Idempotente.
"""

import asyncio

from google.cloud.firestore_v1 import AsyncClient

FORMAT_CATALOG = [
    {
        "format_id": "carrossel",
        "canal": ["instagram", "linkedin"],
        "mecanica": {"min_paginas": 2, "max_paginas": 10, "dimensoes": {"l": 1080, "a": 1350}},
        "estrutura_padrao": ["capa", "conteudo*", "cta"],
        "templates_base": ["base_tipografico", "base_com_imagem", "base_dado"],
    },
    {
        "format_id": "card",
        "canal": ["instagram", "threads"],
        "mecanica": {"min_paginas": 1, "max_paginas": 1, "dimensoes": {"l": 1080, "a": 1350}},
        "estrutura_padrao": ["card_unico"],
        "templates_base": ["base_tipografico", "base_com_imagem"],
    },
    {
        "format_id": "card_noticia",
        "canal": ["instagram", "threads"],
        "mecanica": {"min_paginas": 1, "max_paginas": 1, "dimensoes": {"l": 1080, "a": 1350}},
        "estrutura_padrao": ["card_unico"],
        "templates_base": ["base_noticia"],
    },
    {
        "format_id": "post_linkedin",
        "canal": ["linkedin"],
        "mecanica": {"max_chars": 3000, "dimensoes": None},
        "estrutura_padrao": ["texto"],
        "templates_base": [],
    },
    {
        "format_id": "carrossel_pdf",
        "canal": ["linkedin"],
        "mecanica": {"min_paginas": 2, "max_paginas": 20, "dimensoes": {"l": 1080, "a": 1350}},
        "estrutura_padrao": ["capa", "conteudo*", "cta"],
        "templates_base": ["base_tipografico"],
    },
    {
        "format_id": "thread",
        "canal": ["threads"],
        "mecanica": {"max_chars_per_post": 500, "max_posts": 10},
        "estrutura_padrao": ["gancho", "desenvolvimento*", "cta"],
        "templates_base": [],
    },
    {
        "format_id": "blog",
        "canal": ["blog"],
        "mecanica": {"min_chars": 500, "max_chars": 20000},
        "estrutura_padrao": ["titulo", "intro", "corpo", "conclusao"],
        "templates_base": [],
    },
    {
        "format_id": "reel_renderizado",
        "canal": ["instagram", "tiktok"],
        "mecanica": {"duracao_max_s": 90, "dimensoes": {"l": 1080, "a": 1920}},
        "estrutura_padrao": ["gancho", "conteudo", "cta"],
        "templates_base": ["base_motion"],
    },
    {
        "format_id": "thumbnail_youtube",
        "canal": ["youtube"],
        "mecanica": {"dimensoes": {"l": 1280, "a": 720}},
        "estrutura_padrao": ["thumbnail"],
        "templates_base": ["base_thumbnail"],
    },
    {
        "format_id": "carrossel_resumo_dia",
        "canal": ["instagram"],
        "mecanica": {"min_paginas": 3, "max_paginas": 10, "dimensoes": {"l": 1080, "a": 1350}},
        "estrutura_padrao": ["capa_dia", "noticia*", "cta_newsletter"],
        "templates_base": ["base_resumo_dia"],
    },
]


async def run() -> None:
    db = AsyncClient()

    for fmt in FORMAT_CATALOG:
        await db.document(f"platform/format_catalog/{fmt['format_id']}").set(fmt, merge=True)

    print(f"✓ Catálogo de formatos: {len(FORMAT_CATALOG)} formatos carregados")
    print("✅ Migration 002 completa (idempotente).")


if __name__ == "__main__":
    asyncio.run(run())
