# Inventário — Mapeamento contra a Spec (doc 06 §1)

> **Status: GREENFIELD.** O repositório `aisocialz-platform/` contém apenas a especificação fundacional (`docs/fundacao/`) e nenhum código-fonte, agentes, schemas, integrações ou frontend preexistentes.

## Conclusão

Não há projeto ADK anterior para evoluir. Toda a construção parte do zero, seguindo integralmente os contratos dos docs 00–11.

## Mapeamento (doc 06 §2)

| Item da spec | Já atende | Precisa evoluir | Não existe (criar do zero) |
|---|---|---|---|
| Diretor (orquestrador + conselheiro) | — | — | ✓ |
| Estrategista (candor + slots + experimentos) | — | — | ✓ |
| Radar / Contexto | — | — | ✓ |
| Curador / Editor-chefe (AINewz) | — | — | ✓ |
| Crítico (Fase 2) | — | — | ✓ |
| Roteirista (Fase 2) | — | — | ✓ |
| Redator | — | — | ✓ |
| Designer (templates HTML + render) | — | — | ✓ |
| Editor de vídeo (Fase 2) | — | — | ✓ |
| Revisor (gate formal) | — | — | ✓ |
| Analista (coleta Fase 1, completo Fase 2) | — | — | ✓ |
| Publicador (adapters diretos) | — | — | ✓ |
| Comunidade | — | — | ✓ |
| Guardião de custos | — | — | ✓ |
| Monorepo (doc 11 §2) | — | — | ✓ |
| core_domain (tipos Pydantic) | — | — | ✓ |
| persistence (TenantScope + ScopedRepository) | — | — | ✓ |
| llm_gateway (wrapper + ledger + routing) | — | — | ✓ |
| adapters (contrato + LinkedIn/Meta/Blog) | — | — | ✓ |
| render_client | — | — | ✓ |
| observability | — | — | ✓ |
| svc-agents (Cloud Run, ADK) | — | — | ✓ |
| svc-render (Puppeteer/FFmpeg/Remotion) | — | — | ✓ |
| svc-publisher | — | — | ✓ |
| svc-cockpit-api (BFF) | — | — | ✓ |
| svc-cost-guardian | — | — | ✓ |
| Cockpit (Next.js) | — | — | ✓ |
| Portfolio (Next.js, público) | — | — | ✓ |
| Templates HTML (por marca + base) | — | — | ✓ |
| IaC (Terraform) | — | — | ✓ |
| Migrations (schema idempotentes) | — | — | ✓ |
| CI/CD pipeline | — | — | ✓ |
| Grafo de conteúdo + backfill | — | — | ✓ |
| Schemas Firestore (doc 02) | — | — | ✓ |
| Brand profiles + strategies no Firestore | — | — | ✓ |
| Evento cross-project AINewz (noticia-publicada) | — | — | ✓ |

## Implicações

1. Não há refactor — tudo é construção nova.
2. A regra "evoluir > recriar" (doc 06 §1.2) não se aplica; não há o que preservar.
3. Podemos seguir direto para a Fase 0 (fundação do monorepo + infra + núcleo compartilhado) sem conflitos de migração.
4. Nenhum dado preexistente para migrar — os scripts de `migrations/` começam como seed dos brand profiles e strategies.
