# 06 — Instruções para a IA Construtora

Você está no meio da construção de uma plataforma multi-agente (Diretor + 7 sub-agentes, Google ADK, Vertex AI, Cloud Run, Firestore, Secret Manager, Pub/Sub, frontend Next.js). Estes documentos NÃO descartam esse trabalho — eles o promovem a uma empresa de conteúdo completa. Sua tarefa é integrar, não recomeçar.

## 1. Regras de integração

1. **Inventário antes de código.** Primeiro passo obrigatório: mapear o que já existe (agentes, schemas, integrações, frontend) contra esta especificação e produzir um documento `INVENTARIO.md` com três colunas: *já atende / precisa evoluir / não existe*. Apresentar ao Victor antes de qualquer refactor.
2. **Evoluir > recriar.** Agente existente com papel equivalente (doc 03) recebe o novo contrato via refactor incremental. Só criar do zero o que não existe (Crítico, Revisor formal, Analista, guardião de custos).
3. **Nada de público/tema/tom hardcoded.** Ao tocar qualquer prompt existente, extrair o que for estratégia para `strategies/` e o que for invariante para `brands/`. Este é o refactor mais importante de todos.
4. **Wrapper de LLM primeiro.** Nenhuma feature nova antes do wrapper único de chamadas com ledger de custo (doc 05 §2) — sem ele, não há controle de gasto e o desenvolvimento em si fura o orçamento.
5. **Sandbox por padrão.** As duas marcas nascem em `modo: sandbox`. Promover a produção é decisão explícita do Victor, canal por canal.
6. **AINewz é caixa-preta.** Mudança permitida no projeto AINewz: apenas a publicação do evento `noticia-publicada` + leitura cross-project (doc 01 §1). Não tocar em ingestão, portal, newsletter, nem no publicador de LinkedIn que já funciona.
7. **Custos do build também contam.** Suas próprias chamadas durante desenvolvimento/teste entram no ledger com `agente: "construtora"`. Testes de produção de conteúdo usam Flash.
8. **Migrações de schema versionadas e reversíveis.** Dados existentes do projeto antigo são migrados com script idempotente; nunca mutação manual.

## 2. Mapeamento esperado (validar no inventário)

| Existente (projeto atual) | Vira (esta spec) |
|---|---|
| Diretor orquestrador | Diretor (doc 03) + regras de buffer/degradação |
| Papel de estratégia/calendário | Estrategista com candor + slots + experimentos |
| Agentes de redação/criação | Redator + Roteirista (separar trilhas) |
| Camada de render (Puppeteer/FFmpeg/Remotion) | Serviço de render do Designer/Editor |
| Postiz / integrações de publicação | Adapters próprios com contrato único + idempotência (decidir com o Victor: manter Postiz temporariamente atrás do contrato adapter é aceitável no MVP) |
| Frontend Next.js chat + painel de atividade | Cockpit do CEO (doc 00 §5) |
| — | Crítico, Revisor, Analista, guardião de custos, grafo de conteúdo, memórias, decision log |

## 3. Fases

> **O faseamento canônico está no doc 09 §7** (Fase 1: LinkedIn + Meta + Blog + Google Analytics, todos os formatos, com acervo de mídia e catálogo de formatos; Fase 2: YouTube + TikTok + Email). As descrições de "definição de pronto" abaixo continuam válidas como critério de qualidade de cada entrega.

**Toda fase termina com demo funcional para o Victor.** Antes de tudo, a regra que protege o futuro SaaS:

> **Contrato anti-atalho (doc 09 §2):** nenhuma lógica de marca/canal/usuário em código ou prompt. Toda query carrega `tenant_id` + `brand_id`. Recursos globais (`platform/`) separados de recursos de tenant desde o dia 1. Violar isso para "funcionar mais rápido pro Victor" é o erro mais caro possível — inviabiliza o SaaS sem reescrita.

**Fase 0 — Fundação (sem conteúdo novo).** Inventário; wrapper LLM + ledger + budget + guardião + flag `platform_status`; schemas do doc 02 criados; migração do estado existente; refactor "estratégia fora dos prompts"; brands/strategies dos docs 04/02 carregados (com `[PREENCHER]` pendentes listados para o Victor). *Pronto quando:* uma chamada de teste aparece no ledger, os modos trocam nos gatilhos simulados, e os agentes existentes leem estratégia de Firestore.

**Fase 1 — Memória e trilha autônoma de texto (éozoré em sandbox).** Grafo de conteúdo + backfill do conteúdo já publicado do Victor (ele fornece URLs/exports); retrieval no Redator; Revisor como gate; ciclo completo em sandbox: planejamento → produção de posts/threads → revisão → publicação simulada → preview no cockpit. *Pronto quando:* um post simulado referencia corretamente um conteúdo antigo do grafo com link acionável.

**Fase 2 — Visual + AINewz.** Templates HTML das duas marcas + render Puppeteer; evento cross-project + score editorial + produção de cards/carrosséis do AINewz em sandbox; adapters reais de IG/Threads; promoção a produção dos canais de menor risco (Threads, blog) com aprovação do Victor.

**Fase 3 — Vídeo e trilha colaborativa.** Pipeline do bucket (transcrição → atom → cortes → derivados); Roteirista + fila do CEO + sessão a 4 mãos no cockpit; adapter YouTube.

**Fase 4 — Inteligência.** Analista completo (coleta diária, learnings, experimentos); Crítico no planejamento; retro semanal + curadoria de memórias + relatório do CEO; decision log alimentado pelo cockpit; "modo férias".

## 4. Definição de pronto (toda fase)

Checagem dupla: (a) funcional — o demo roda fim-a-fim em sandbox; (b) sistêmica — ledger registrou os custos da fase, `platform_status` é respeitado por todo job novo, nenhum prompt novo contém estratégia hardcoded, e logs permitem reconstruir por que cada peça foi produzida (estratégia versão X, slot Y, agente Z).

## 5. Perguntas abertas que exigem o Victor (não decidir sozinha)

> Resolvidas no doc 08: comunidade (auto/manual + score), crise (score de severidade + kill switch), guardrail de injection, compliance editorial (escopo do AINewz), tokens/quotas, golden set + regra do legado, orçamento build vs operação, backup semanal. Restam:

1. Postiz atrás do contrato adapter no MVP, ou adapters diretos desde já?
2. ~~CTA de fundo de funil~~ **RESOLVIDO:** fase inicial = crescimento de audiência (éozoré: seguidores/inscritos; AINewz: assinantes da newsletter). `objetivo_de_conversao.tipo = "audiencia"` (doc 02). Quando houver produto (mentoria/curso), trocar para `"receita"` sem refatorar.
3. Curadoria do few-shot de voz: quais peças do legado recebem `few_shot_aprovado: true` (doc 08 §6) — apenas as que o Victor marcar; e exports para backfill do grafo.
4. Hexas da paleta, tipografia e handles/URLs `[PREENCHER]` do doc 04.
5. Mecanismo atual de LinkedIn/newsletter do AINewz: manter como está e só adicionar formatos novos, ou migrar para os adapters deste projeto?
