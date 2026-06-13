# 01 — Arquitetura GCP

## 1. Topologia de projetos

```
┌─────────────────────────────────────────┐   ┌──────────────────────────┐
│  PROJETO: plataforma-conteudo (este)    │   │  PROJETO: ainewz         │
│                                         │   │  (existente, NÃO tocar   │
│  Cloud Run (agentes ADK, render, APIs)  │   │   na lógica interna)     │
│  Vertex AI (Gemini + Claude + embeds)   │   │                          │
│  Firestore (estado, schemas doc 02)     │◄──┤  + Pub/Sub topic:        │
│  Cloud Storage (vídeos, assets, HTML)   │   │    "noticia-publicada"   │
│  Pub/Sub (eventos internos)             │   │  + Endpoint/Firestore    │
│  Cloud Scheduler (heartbeat)            │   │    read-only p/ conteúdo │
│  Secret Manager (credenciais por marca) │   │    completo da notícia   │
│  Vertex AI Vector Search (grafo)        │   └──────────────────────────┘
│  Cloud Billing Budget + guardião custos │
│  Next.js (cockpit, já existente)        │
└─────────────────────────────────────────┘
```

**Decisão de fronteira:** o AINewz permanece projeto separado e soberano sobre ingestão/portal/newsletter/LinkedIn que já funcionam. A integração se limita a:

1. O AINewz publica um evento `noticia-publicada` num topic Pub/Sub **do próprio projeto AINewz** (payload mínimo: id, título, resumo, url, tags, timestamp). É a única mudança permitida lá — pequena, aditiva, sem risco.
2. Este projeto cria uma **subscription cross-project** nesse topic, usando uma service account dedicada (`sa-ainewz-reader@plataforma-conteudo.iam`) com papel `roles/pubsub.subscriber` concedido no projeto AINewz.
3. Para conteúdo completo da notícia, a mesma SA recebe leitura no recurso onde o AINewz guarda artigos (Firestore read-only na collection de notícias OU um endpoint HTTP autenticado — escolher o que já existir; preferir não criar API nova).

A marca `ainewz` (distribuição multi-formato) roda **neste** projeto, consumindo o portal como fonte. Razão: reuso de todo o time de agentes, grafo, FinOps e cockpit.

## 2. Serviços e responsabilidades

| Serviço | Uso |
|---|---|
| **Cloud Run** | (a) serviço dos agentes ADK (já existe — evoluir, não recriar); (b) serviço de render: Puppeteer para HTML→imagem, FFmpeg/Remotion para vídeo, container separado com CPU/mem maiores e `min-instances=0`; (c) API do cockpit. |
| **Vertex AI** | Gemini 2.5 Flash (tarefas estruturais), Gemini 2.5 Pro e Claude via Vertex (criativo final — ver routing no doc 03 §1). Embeddings: `text-embedding` mais barato disponível. |
| **Firestore** | Todo o estado (schemas no doc 02). Modo nativo. |
| **Vector Search** | Índice do grafo de conteúdo. Alternativa de MVP barato: busca vetorial no próprio Firestore (find_nearest) — aceitável até ~10k nós; só migrar para Vector Search se latência/recall degradar. **Começar pelo Firestore.** |
| **Cloud Storage** | Buckets: `videos-brutos` (upload do Victor, dispara evento), `assets-renderizados`, `templates-html` (versionado também em git). |
| **Pub/Sub** | Topics internos: `video-recebido`, `item-produzido`, `item-aprovado`, `publicacao-executada`, `custo-alerta`. |
| **Cloud Scheduler** | Jobs do heartbeat (doc 00 §4). Todos os jobs checam a flag global `platform_status` antes de executar (ver doc 05). |
| **Secret Manager** | Credenciais escopadas por tenant/marca/canal: `{tenant}--{brand}--{canal}--credentials` (doc 09 §8). Isolamento entre tenants. Agentes nunca recebem segredos em prompt; só o `svc-publisher` resolve em runtime. Tokens Meta exigem refresh programático (doc 08 §5). |
| **Cloud Billing Budgets** | Orçamento mensal com thresholds → Pub/Sub → função guardiã (doc 05). |

## 3. Publicação: adapters próprios

Contrato único (o resto do sistema não conhece APIs específicas):

```python
class ChannelAdapter(Protocol):
    def publish(self, brand: str, payload: PublishPayload) -> PublishResult
    def get_metrics(self, brand: str, post_ref: str) -> MetricsSnapshot
    def validate(self, payload: PublishPayload) -> list[ValidationIssue]
```

Adapters da fase inicial: `linkedin`, `instagram` (feed/carrossel/reels), `threads`, `youtube` (vídeo + shorts + comunidade), `blog` (commit/API do site próprio), `newsletter` (reusar mecanismo do AINewz onde aplicável). `tiktok` é só um novo adapter no futuro — nenhuma outra mudança.

Regras de confiabilidade do Publicador:
- **Idempotência obrigatória**: todo publish gera `idempotency_key = hash(brand, canal, content_id, slot)`; antes de postar, checa em `publications/` se a key já tem sucesso. Retry jamais duplica post.
- Retries com backoff exponencial, máx 3; falha definitiva → item volta a `agendado` + alerta humano.
- `validate()` roda no momento do agendamento (limites de caracteres, dimensões de mídia, política do canal), não na hora de postar.

## 4. Segurança e IAM

- Uma SA por função: agentes, render, publicador, guardião de custos, cockpit. Princípio do menor privilégio.
- O Publicador é a única SA com acesso aos secrets de canais.
- Cockpit autenticado (Identity Platform ou IAP) — é painel de uma pessoa, não complicar.
- Logs de toda decisão de publicação (quem decidiu, com que estratégia/versão, custo) — auditável pelo decision log (doc 02).

## 5. Ambientes

`staging` é uma flag, não um projeto: marcas têm campo `modo: producao | sandbox`. Em sandbox, o Publicador escreve o resultado em `publications/` com `simulado: true` e renderiza preview no cockpit, sem chamar APIs externas. **Toda mudança de prompt/agente roda 1 ciclo em sandbox antes de produção.**

## 6. Portfólio do Victor: separado da plataforma (decisão fechada)

O portfólio é um ativo público da marca éozoré; a plataforma é a fábrica multi-marca. Decisão: **monorepo, deploys separados**.

- Estrutura: `apps/portfolio` (público, sem segredos, deploy/billing próprio), `apps/cockpit` (autenticado, deploy próprio dentro do projeto da plataforma), `packages/ui` (componentes compartilhados — reaproveitar o chat + painel de atividade já construídos).
- O cockpit e qualquer superfície administrativa SAEM do portfólio. O portfólio fica 100% público.
- O portfólio se relaciona com a plataforma apenas como: (a) **destino de publicação** — o adapter `blog` publica nele; (b) **consumidor read-only** — pode exibir "últimos conteúdos" consumindo uma API do grafo de conteúdo.
- Custos do portfólio NÃO entram no ledger/orçamento da plataforma (doc 05).
- Migração: mover o cockpit para `apps/cockpit` na Fase 0 (doc 06), antes de novas features de painel.
