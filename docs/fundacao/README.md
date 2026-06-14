# README — Pacote Fundacional da Plataforma

Especificação para a IA construtora turbinar o projeto existente (Diretor + sub-agentes, Google ADK, GCP/Vertex). **Não recomeçar — integrar.** Ponto de entrada de execução: **doc 06**.

## Ordem de leitura
1. **09 — Modelo de Produto** *(ler primeiro; reorienta tudo)*: multi-tenant, times contratáveis, Diretor-conselheiro, KB de marketing, faseamento canônico.
2. **00 — Visão e Modelo Operacional**: princípios, duas trilhas, heartbeat, cockpit.
3. **06 — Instruções para a Construtora**: inventário-antes-de-código, mapeamento, fases, contrato anti-atalho, perguntas abertas.
4. **03 — Contratos dos Agentes**: routing de modelos (Vertex: `claude-opus-4-6` / `claude-sonnet-4-6`), candor, e os agentes (incl. novos: Diretor-conselheiro, Radar, Curador, Crítico, Revisor, Analista, Comunidade).
5. **02 — Schemas** · **01 — Arquitetura GCP** · **04 — Brand Profiles**
6. **10 — Formatos, Templates e Acervo** · **07 — Render e Template Studio**
7. **05 — FinOps** · **08 — Comunidade, Crise e Guardrails**
8. **11 — Arquitetura Detalhada** *(implementação: monorepo, contratos Python, fluxos ponta-a-ponta; ler ao começar a codar)*

## Precedência em conflito
**09 → 08 → demais.**

## Decisões-chave já fechadas
- Plataforma-produto multi-marca; Victor é o 1º cliente; SaaS é o horizonte. **Zero lógica de marca em código/prompt** (contrato anti-atalho).
- Vertex: Opus 4.6 + Sonnet 4.6 (nome completo fixado; parametrizável p/ 4.7/4.8). IDE espelha.
- Times contratáveis e desativáveis; core sempre on.
- Diretor = orquestrador **+ conselheiro de marketing** do CEO.
- Radar = eventos de calendário universal + calendário editorial do nicho tech/IA, filtrados por **força-da-ponte** (anti gancho forçado).
- AINewz: portal recebe tudo; curadoria em 2 níveis (sério: news/LinkedIn; social: formatos novos).
- Guardrail de sensível = **radar, não muro** (preserva tese forte, corrige deslize acidental).
- Acervo de mídia vetorizado, preenchido por humano e agente; **direitos = risco do CEO na V1** (verificação é feature futura).
- Formatos em 4 camadas; CEO aprova o conjunto de templates, não desenha pixel; time de revisão de templates evolui o visual como proposta.
- Vídeo automatizado = só motion na Fase 1-2; vídeos gravados manuais; time de edição por IA + repositório = futuro.
- FinOps: gatilhos R$200/400/600 só p/ operação; build é à parte.
- Faseamento: **Fase 1** LinkedIn+Meta+Blog+GA (todos formatos, fundo); **Fase 2** YouTube+TikTok+Email.

## Pendências do Victor (não bloqueiam a Fase 0)
- `[PREENCHER]` nos docs 02 (CTA de fundo de funil + metas), 04 (hexas, tipografia, few-shot, topic AINewz), 06 (perguntas abertas).
- Reenviar o HTML-base de template (upload falhou) para virar o 1º template do catálogo.
