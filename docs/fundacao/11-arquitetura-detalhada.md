# 11 — Arquitetura Detalhada (repositórios, contratos, fluxos)

> Documento técnico de implementação. Princípio: **contratos e estrutura em detalhe real; lógica interna como stub**. Os contratos (interfaces, schemas de mensagem, assinaturas) são normativos — a construtora deve respeitá-los à risca, pois são o que mantém os módulos desacoplados e o sistema multi-tenant (doc 09 §2). A lógica dentro dos métodos é orientação, não lei. Linguagem: Python 3.12 (agentes/serviços); cockpit em Next.js consome via API HTTP (fronteira tratada como contrato de API, §9).
>
> Não conflita com docs 00–10; materializa-os. Em divergência de regra de negócio, os docs anteriores vencem; em divergência de contrato técnico, este vence.

## 1. Visão de componentes

```
┌───────────────────────────── GCP: projeto plataforma-conteudo ──────────────────────────────┐
│                                                                                              │
│  Cloud Scheduler ──► Pub/Sub (eventos) ──► Cloud Run services                                │
│                                                                                              │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  ┌─────────────────┐  │
│  │ svc-agents │  │ svc-render  │  │ svc-publisher│  │ svc-cockpit-api│  │ svc-cost-guardian│ │
│  │ (ADK)      │  │ (Puppeteer/ │  │ (adapters)   │  │ (BFF do Next)  │  │ (determinístico) │ │
│  │            │  │  FFmpeg/    │  │              │  │                │  │                  │ │
│  │            │  │  Remotion)  │  │              │  │                │  │                  │ │
│  └─────┬──────┘  └──────┬──────┘  └──────┬───────┘  └───────┬───────┘  └────────┬─────────┘  │
│        │                │                │                  │                   │            │
│        └────────────────┴────────────────┴──────┬───────────┴───────────────────┘            │
│                                                  │                                            │
│   Firestore (estado, doc 02)   Cloud Storage (vídeos/assets/templates)   Vertex AI (LLM+emb) │
│   Secret Manager (credenciais)  Cloud Billing Budget                                          │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
        ▲                                                            │
        │ Pub/Sub cross-project: noticia-publicada                   │ APIs externas
   ┌────┴─────────────────┐                              ┌───────────┴───────────────────┐
   │ projeto ainewz       │                              │ LinkedIn, Meta, Blog, (YT,TT)  │
   └──────────────────────┘                              └────────────────────────────────┘
```

Cinco serviços Cloud Run. `svc-agents` hospeda todos os agentes ADK (um serviço, múltiplos agentes — não um Cloud Run por agente, custo desnecessário na V1). `svc-render`, `svc-publisher`, `svc-cockpit-api` e `svc-cost-guardian` são serviços dedicados por terem perfis de recurso/escala/segurança distintos.

## 2. Estrutura do monorepo

```
plataforma-conteudo/                      # monorepo (doc 01 §6: deploys separados)
├── README.md
├── pyproject.toml                        # workspace Python (uv/poetry); ruff, mypy
├── packages/                             # bibliotecas compartilhadas (Python)
│   ├── core_domain/                      # tipos de domínio, SEM dependência de infra
│   │   └── src/core_domain/
│   │       ├── models.py                 # BacklogItem, ContentNode, Slot, Brand... (§3)
│   │       ├── enums.py                   # Status, Funil, Formato, Canal, TeamId
│   │       ├── messages.py               # contratos de mensagem entre agentes (§4)
│   │       └── recommendation.py          # contrato de candor (§4.3)
│   ├── llm_gateway/                      # wrapper único de LLM + ledger (§6) — NINGUÉM chama Vertex direto
│   │   └── src/llm_gateway/
│   │       ├── client.py                  # LlmGateway
│   │       ├── routing.py                 # resolve modelo por tarefa + modo de custo
│   │       └── pricing.py                 # tabela versionada (lê platform/pricing)
│   ├── persistence/                      # acesso a Firestore com escopo de tenant OBRIGATÓRIO (§5)
│   │   └── src/persistence/
│   │       ├── repository.py              # ScopedRepository[T] genérico
│   │       ├── vector.py                  # busca vetorial (grafo + acervo) §7
│   │       └── scope.py                   # TenantScope — toda query passa por aqui
│   ├── adapters/                         # contrato + implementações de canal (§8)
│   │   └── src/adapters/
│   │       ├── base.py                    # ChannelAdapter (Protocol)
│   │       ├── linkedin.py  meta.py  blog.py
│   │       └── registry.py                # resolve adapter por canal, respeita team_subscriptions
│   ├── render_client/                    # cliente do svc-render (tipos de request/response) §8.4
│   └── observability/                    # logging estruturado, tracing, decision_log helper
├── services/
│   ├── agents/                           # svc-agents (ADK)
│   │   └── src/agents/
│   │       ├── base.py                    # PlatformAgent (base de todo agente) §4.1
│   │       ├── diretor.py  estrategista.py  critico.py  radar.py  curador.py
│   │       ├── redator.py  roteirista.py  designer.py  editor_video.py
│   │       ├── revisor.py  analista.py  comunidade.py
│   │       ├── orchestration.py           # ADK: grafo de orquestração, heartbeat handlers
│   │       └── main.py                    # entrypoint Cloud Run (HTTP + Pub/Sub push)
│   ├── render/                           # svc-render (Node interno p/ Puppeteer/Remotion + API Py)
│   ├── publisher/                        # svc-publisher
│   ├── cockpit_api/                      # svc-cockpit-api (BFF)
│   └── cost_guardian/                    # svc-cost-guardian
├── apps/
│   ├── cockpit/                          # Next.js (doc 09 §5) — consome cockpit_api
│   └── portfolio/                        # site público (doc 01 §6)
├── templates/                            # templates HTML por marca + base (doc 10) — versionados
│   ├── _base/{formato}/...                # templates-base brandáveis
│   ├── eozore/...   ainewz/...
├── infra/                                # IaC (Terraform): Cloud Run, Pub/Sub, Scheduler, IAM, Budget
│   ├── topics.tf  scheduler.tf  iam.tf  budget.tf  firestore_indexes.tf
└── migrations/                          # migrações de schema idempotentes (doc 06 §1)
```

Regras de dependência (impostas por lint/CI): `core_domain` não importa nada de infra; `services/*` dependem de `packages/*`, nunca o contrário; um adapter de canal nunca importa outro; agentes nunca chamam Vertex sem ser via `llm_gateway`; nenhum serviço acessa Firestore sem ser via `persistence` (garante escopo de tenant).

## 3. Tipos de domínio (`core_domain/models.py`)

Modelos imutáveis (Pydantic v2). Espelham o doc 02. Trechos normativos:

```python
from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, Field

class Canal(StrEnum):
    LINKEDIN = "linkedin"; INSTAGRAM = "instagram"; FACEBOOK = "facebook"
    THREADS = "threads"; BLOG = "blog"; YOUTUBE = "youtube"; TIKTOK = "tiktok"

class Funil(StrEnum):
    TOPO = "topo"; MEIO = "meio"; FUNDO = "fundo"

class ItemStatus(StrEnum):
    IDEIA = "ideia"; BRIEFING = "briefing"; PRODUCAO = "producao"; REVISAO = "revisao"
    AGUARDANDO_CEO = "aguardando_ceo"; APROVADO = "aprovado"; AGENDADO = "agendado"
    PUBLICADO = "publicado"; REJEITADO = "rejeitado"; QUARENTENA = "quarentena"

class Autonomia(StrEnum):
    DRAFT_ONLY = "draft_only"; APPROVE_REQUIRED = "approve_required"; AUTO_PUBLISH = "auto_publish"

# Identidade de escopo — presente em TODA entidade de tenant (doc 09 §2)
class Scope(BaseModel):
    tenant_id: str
    brand_id: str

class BacklogItem(BaseModel):
    id: str
    scope: Scope
    tipo: str                       # ver doc 02 (carrossel, post_linkedin, ...)
    pilar: str
    funil: Funil
    fonte: "Fonte"
    requer_ceo: bool = False
    status: ItemStatus = ItemStatus.IDEIA
    slot_alvo: str | None = None
    referencias_grafo: list[str] = Field(default_factory=list)
    artefatos: "Artefatos"
    risco_sensibilidade: "RiscoSensibilidade | None" = None   # doc 08 §3b
    historico: list["EventoProducao"] = Field(default_factory=list)

class ContentNode(BaseModel):              # content_graph (doc 02 + doc 10 §6)
    id: str
    scope: Scope
    titulo: str
    conceitos: list[str]
    depende_de: list[str] = Field(default_factory=list)
    pilar: str; funil: Funil; formato: str; canal: Canal
    url: str | None = None
    como_referenciar: dict[str, str] = Field(default_factory=dict)
    template_id: str | None = None         # qual template gerou a peça
    template_versao: str | None = None
    assets_usados: list[str] = Field(default_factory=list)
    performance: "Performance"
    few_shot_aprovado: bool = False         # doc 08 §6 — só CEO marca
    embedding: list[float] | None = None

class MediaAsset(BaseModel):               # media_assets (doc 10 §4)
    id: str
    scope: Scope
    tipo: str                              # imagem|video|logo
    fonte: str                             # humano_upload|agente_pesquisa|ainewz_noticia|video_ia_futuro
    url: str
    tags: list[str]
    descricao: str
    embedding: list[float] | None = None
    ref_origem: str | None = None
```

## 4. Contratos entre agentes

### 4.1 Base de todo agente (`services/agents/base.py`)

```python
from abc import ABC, abstractmethod
from core_domain.messages import AgentRequest, AgentResponse
from llm_gateway import LlmGateway
from persistence import ScopedRepository

class PlatformAgent(ABC):
    """Base de todo agente. Garante: escopo de tenant, gateway de LLM (nunca Vertex direto),
    e acesso ao KB/memória. A lógica específica vive em handle()."""
    agent_id: str
    team: str                       # doc 09 §3 — a qual time pertence (gating por subscription)

    def __init__(self, gateway: LlmGateway, repo: ScopedRepository, kb: "KnowledgeBase"):
        self._gateway = gateway; self._repo = repo; self._kb = kb

    @abstractmethod
    async def handle(self, req: AgentRequest) -> AgentResponse:
        """Recebe tarefa, devolve resultado. Implementação por agente.
        REGRA: todo prompt monta contexto a partir de config+KB+grafo — NUNCA hardcode de marca."""
        ...

    # helper comum: monta o bloco de contexto cacheável (estratégia ativa + brand profile + voz + KB)
    async def _build_context(self, scope) -> "AgentContext": ...
```

### 4.2 Mensagem entre agentes (`core_domain/messages.py`)

O handoff entre agentes é sempre por mensagem tipada via Pub/Sub (assíncrono) ou chamada direta dentro do ADK (síncrono). Mesmo payload nos dois casos:

```python
class AgentRequest(BaseModel):
    request_id: str
    scope: Scope
    task: str                       # "produzir_post" | "revisar" | "pontuar_noticia" | ...
    item_id: str | None = None      # referência ao BacklogItem quando aplicável
    payload: dict                   # dados específicos da task
    trace_id: str                   # observabilidade ponta-a-ponta

class AgentResponse(BaseModel):
    request_id: str
    ok: bool
    output: dict                    # resultado (texto, ids gerados, score, ...)
    cost_brl: float                 # custo agregado desta operação (vem do gateway)
    next: list["AgentRequest"] = Field(default_factory=list)  # handoffs propostos
    notes: str | None = None
```

### 4.3 Contrato de candor (`core_domain/recommendation.py`)

Toda recomendação de agente estratégico (Diretor, Estrategista, Crítico, Analista, Radar) DEVE retornar este tipo — sem os quatro campos, o Diretor rejeita (doc 03 §2):

```python
class Recommendation(BaseModel):
    posicao: str                    # recomendação direta, sem hedging
    evidencia: list[str]            # refs a content_graph/learnings/decision_log; vazio => declarar intuição
    contra_argumento: str           # o melhor caso CONTRA a própria posição
    confianca: float = Field(ge=0, le=1)
    o_que_mudaria_confianca: str

    def is_valid(self) -> bool:
        return bool(self.posicao and self.contra_argumento and self.o_que_mudaria_confianca)
```

### 4.4 Contratos específicos importantes

```python
# Radar (doc 03) -> Estrategista
class MomentoRelevante(BaseModel):
    evento: str; tipo: str          # calendario_universal | calendario_nicho | noticiario
    data_ou_janela: str
    forca_da_ponte: float = Field(ge=0, le=1)   # conexão genuína com um pilar
    pilar_conectado: str | None
    recomendacao: str               # "usar" | "ignorar" + justificativa

# Curador (doc 03) -> backlog
class NoticiaCurada(BaseModel):
    noticia_id: str
    score_editorial: float
    nivel: str                      # "serio" (news/linkedin) | "social" (formatos novos)
    formatos_sugeridos: list[str]
    angulo: str

# Guardrail de sensibilidade (doc 08 §3b) — anexado ao item antes de publicar
class RiscoSensibilidade(BaseModel):
    nivel: str                      # baixo | medio | alto
    tipo: str                       # intencional (tese forte) | acidental (deslize)
    publico_em_risco: str
    diagnostico: str
```

## 5. Persistência com escopo obrigatório (`persistence/`)

O ponto onde o multi-tenant é garantido por construção: é **impossível** ler/escrever sem escopo.

```python
class TenantScope:
    """Resolve o caminho Firestore. Toda operação passa por aqui."""
    def __init__(self, tenant_id: str, brand_id: str | None = None):
        self.tenant_id = tenant_id; self.brand_id = brand_id
    def collection_path(self, name: str) -> str:
        if name in GLOBAL_COLLECTIONS:           # platform/* (doc 02)
            return f"platform/{name}"
        if name in TENANT_COLLECTIONS:           # cost_ledger, team_subscriptions, config...
            return f"tenant/{self.tenant_id}/{name}"
        assert self.brand_id, f"{name} exige brand_id"
        return f"tenant/{self.tenant_id}/brands/{self.brand_id}/{name}"

class ScopedRepository[T: BaseModel]:
    def __init__(self, db, scope: TenantScope, model: type[T], collection: str): ...
    async def get(self, id: str) -> T | None: ...
    async def put(self, entity: T) -> None: ...           # valida entity.scope == self.scope
    async def query(self, **filters) -> list[T]: ...
    # NÃO existe método sem escopo. Query cross-tenant é proibida no código de produto.
```

## 6. Gateway de LLM + ledger (`llm_gateway/`)

Nenhum agente chama Vertex direto (doc 05 §2). O gateway resolve modelo, aplica modo de custo, registra no ledger e impõe tetos.

```python
class TaskKind(StrEnum):
    ESTRUTURAL = "estrutural"        # -> Gemini Flash
    ANALITICA = "analitica"          # -> Gemini Pro | Sonnet 4.6
    CRIATIVA = "criativa"            # -> Opus 4.6 (passe final) / Sonnet (volume)
    CONSELHO = "conselho"            # -> Opus 4.6
    EMBEDDING = "embedding"

class LlmGateway:
    async def complete(self, *, scope, agent_id, task_kind: TaskKind,
                       messages: list[dict], item_id: str | None = None,
                       conta: str = "operacao") -> "LlmResult":
        """1) checa platform_status (paused -> aborta) e modo (economia -> rebaixa routing)
           2) resolve modelo (routing.py) por task_kind + modo
           3) checa teto por item e teto diário da marca (doc 05 §2) -> excedeu, levanta BudgetExceeded
           4) chama Vertex (claude-opus-4-6 / claude-sonnet-4-6 / gemini-*)
           5) calcula custo (pricing.py) e grava cost_ledger com conta=operacao|build
           6) incrementa contador do mês; se cruzou gatilho, publica custo-alerta"""
        ...

class LlmResult(BaseModel):
    text: str
    model_used: str
    cost_brl: float
    tokens_in: int; tokens_out: int
```

Routing parametrizável em `platform/model_routing` (doc 03 §0) — trocar 4.6→4.7/4.8 é editar config, não código.

## 7. Busca vetorial (`persistence/vector.py`)

Grafo de conteúdo e acervo de mídia usam o MESMO mecanismo (Firestore `find_nearest` na V1 — doc 02/doc 10 §6; migrar para Vertex Vector Search só se a escala exigir).

```python
class VectorSearch:
    async def nearest_content(self, scope, query_embedding, k=5,
                              conceitos: list[str] | None = None) -> list[ContentNode]:
        """Retrieval do grafo: usado por Redator/Roteirista antes de produzir (doc 02 regra 2).
        Combina similaridade vetorial + match de conceitos."""
        ...
    async def nearest_assets(self, scope, query_embedding, k=3,
                             min_score: float) -> list[MediaAsset]:
        """Designer busca imagem do acervo por tema (doc 10 §3). Abaixo de min_score -> [] (cai no tipográfico)."""
        ...
```

## 8. Contratos de serviço

### 8.1 ChannelAdapter (`adapters/base.py`) — doc 01 §3

```python
from typing import Protocol

class PublishPayload(BaseModel):
    scope: Scope
    canal: Canal
    content_id: str
    slot_id: str
    texto: str | None = None
    midias: list[str] = Field(default_factory=list)   # paths gs:// já renderizados
    meta: dict = Field(default_factory=dict)           # ex.: primeiro_comentario, titulo_yt
    idempotency_key: str                               # hash(scope,canal,content_id,slot) — doc 01 §3

class PublishResult(BaseModel):
    ok: bool; post_url: str | None; post_ref: str | None; erro: str | None = None

class MetricsSnapshot(BaseModel):
    post_ref: str; coletado_em: datetime; metricas: dict   # normalizado pelo Analista

class ValidationIssue(BaseModel):
    campo: str; problema: str

class ChannelAdapter(Protocol):
    canal: Canal
    def validate(self, payload: PublishPayload) -> list[ValidationIssue]: ...
    async def publish(self, payload: PublishPayload) -> PublishResult: ...
    async def get_metrics(self, post_ref: str, scope: Scope) -> MetricsSnapshot: ...
```

Regras: o adapter resolve credenciais via Secret Manager em runtime (nunca recebe segredo em payload), no caminho escopado `{tenant}--{brand}--{canal}--credentials` (doc 09 §8); é a única SA com acesso aos secrets de canal; `publish` é idempotente (checa `publications/{idempotency_key}` antes). **Adapter da Meta (Instagram/Facebook/Threads): DEVE implementar o fluxo de long-lived token + refresh programático** — esses tokens expiram em ~60 dias; sem refresh o canal morre sozinho (o job de saúde de credenciais, doc 08 §5, dispara a renovação). `registry.py` recusa entregar adapter de time inativo (`team_subscriptions`, doc 09 §3).

### 8.2 Serviço de render (`render_client/`) — doc 07, doc 10

```python
class RenderRequest(BaseModel):
    scope: Scope
    template_id: str; template_versao: str
    formato: str                          # carrossel | card | thumbnail | reel_render | ...
    dados: dict                           # variáveis do template (texto)
    assets: list[str] = Field(default_factory=list)   # gs:// de imagens do acervo (doc 10 §6)
    saida: str                            # png | jpg | mp4
    dimensoes: tuple[int, int]

class RenderResult(BaseModel):
    ok: bool; outputs: list[str]          # gs:// dos arquivos gerados
    overflow_detectado: bool; custo_brl: float
```

### 8.3 Publicador (orquestração da fila) — código determinístico, sem LLM (doc 03)
Lê `schedule/` na janela do canal → monta `PublishPayload` → `adapter.validate()` → `adapter.publish()` → cria/atualiza `ContentNode` com `url` real → publica `publicacao-executada`. Retry com backoff (máx 3); falha definitiva → item volta a `agendado` + alerta.

## 9. Fronteira cockpit ↔ backend (contrato de API)

O cockpit (Next.js) nunca toca Firestore nem agentes direto — fala só com `svc-cockpit-api` (BFF) por HTTP/JSON autenticado. Endpoints normativos da V1:

```
GET  /api/brands                         -> marcas do tenant + status
GET  /api/backlog?status=&brand=         -> esteira de produção (doc 09 §5)
GET  /api/approvals                      -> fila do CEO
POST /api/approvals/{id}                 -> { acao: aprovar|editar|rejeitar, motivo? }  (grava decision_log)
GET  /api/schedule?brand=&semana=        -> calendário
GET  /api/report/weekly?brand=           -> relatório do Diretor
GET  /api/teams                          -> team_subscriptions (sala de contratação)
POST /api/teams/{team_id}                -> { ativo: bool }
GET  /api/connections?brand=             -> status de credenciais por canal (conectado|expira_em|desconectado) (doc 09 §8)
POST /api/connections/{canal}/oauth/start -> inicia OAuth -> retorna url de autorização
GET  /api/connections/{canal}/oauth/callback -> recebe code, troca por token, grava Secret Manager escopado
POST /api/connections/{canal}/manual     -> { chave } para canais sem OAuth (grava secret escopado)
GET  /api/media?brand=                   -> acervo
POST /api/media                          -> upload de asset (humano) -> dispara vetorização
GET  /api/templates?brand=               -> Template Studio (galeria)
POST /api/chat/diretor                   -> mensagem ao Diretor-conselheiro (stream)
GET  /api/cost                           -> gasto do mês vs gatilhos (doc 05 §5)
```

Toda rota injeta `tenant_id` do token de auth — o cockpit nunca envia `tenant_id` no corpo (evita spoofing). Na V1, um tenant; na virada SaaS, o token carrega o tenant do usuário logado, e nada mais muda.

## 10. Fluxos ponta-a-ponta

### 10.1 Notícia AINewz → publicação multi-formato (autônomo)
```
1. projeto ainewz publica `noticia-publicada` (Pub/Sub cross-project)
2. svc-agents (push subscription) -> Curador.handle(task="pontuar_noticia")
   - guardrail injection (doc 08 §3): texto da notícia entra demarcado como DADO
   - retorna NoticiaCurada (score, nivel, formatos_sugeridos)
3. se score < minimo -> descarta. senão -> cria BacklogItem(s) por formato sugerido
4. Redator.handle(task="produzir") por item:
   - VectorSearch.nearest_content (referências do grafo, doc 02 regra 2)
   - LlmGateway.complete(task_kind=CRIATIVA)  -> texto nativo do canal
5. Designer.handle(task="montar_visual") se formato pede imagem:
   - VectorSearch.nearest_assets (imagem da notícia/acervo, doc 10 §3)
   - render_client.render(...) -> gs:// das imagens
6. Revisor.handle(task="revisar"):
   - voz + factualidade (afirmação rastreável à fonte) + referências + RiscoSensibilidade
   - reprova -> volta ao produtor; aprova -> status=aprovado
7. Estrategista aloca slot (janela do canal) -> status=agendado
8. svc-publisher na janela -> adapter.publish -> ContentNode criado com url
9. Analista (diário) -> get_metrics -> atualiza performance -> realimenta score do Curador
```

### 10.2 Vídeo gravado (éozoré) → derivados (trilha colaborativa)
```
1. Victor sobe vídeo no bucket videos-brutos -> evento `video-recebido`
2. Editor_video.handle: transcrição (Gemini multimodal) -> content atom -> cortes (timestamps)
3. derivados viram BacklogItems (cortes_short, post, carrossel, blog) -> trilha autônoma
   (do passo 4 da 10.1 em diante). Roteiro prévio foi a 4 mãos (fila do CEO) ANTES da gravação.
```

### 10.3 Rodada de planejamento semanal (heartbeat)
```
Scheduler (dom 18h) -> orchestration.weekly_planning(scope por marca ativa):
1. Analista -> leitura da semana (learnings novos, performance, experimentos sugeridos)
2. Radar -> list[MomentoRelevante] (calendário universal + nicho, força-da-ponte)
3. Estrategista -> calendário (Recommendation por decisão) reservando ~20% p/ experimentos
4. Critico -> red-team (cada ataque com evidência); Estrategista refuta/acata
5. Diretor -> consolida, valida candor, escreve resumo -> approvals (fila do CEO)
   - sem resposta em 24h -> aplica conforme autonomia (doc 00 §4)
```

## 11. Observabilidade e segurança (resumo operacional)
- **trace_id** propaga por toda cadeia (AgentRequest.trace_id) -> reconstrói "por que esta peça existe" (estratégia vN, slot, agentes, custo). Atende a "definição de pronto" do doc 06 §4.
- **decision_log** escrito via helper de `observability` em toda decisão humana/Diretor.
- **IAM**: uma SA por serviço (doc 01 §4); só `svc-publisher` lê secrets de canal; `svc-cost-guardian` é o único que altera `platform_status`.
- **CI**: lint de dependências (§2), mypy estrito em `core_domain`/contratos, e teste que falha se algum acesso a Firestore burlar `persistence` ou alguma chamada Vertex burlar `llm_gateway`.

## 12. Ordem de construção (casa com doc 06 / doc 09 §7)
```
Fase 0: monorepo + core_domain + persistence(scope) + llm_gateway(ledger) + infra base + migrations
Fase 1: adapters(linkedin/meta/blog) + render + vector + agentes(core+radar+curador+revisor+comunidade)
        + cockpit_api + cockpit V1 + acervo + catálogo de formatos + GA
Fase 2: adapters(youtube/tiktok) + editor_video + email + time de revisão de templates (proposta auto)
```

## 13. Decisões de arquitetura registradas (ADRs)

Decisões deliberadas que a construtora NÃO deve reverter sem motivo explícito. "Consertar" qualquer uma destas sem o gatilho correspondente é regressão.

### ADR-001 — Monorepo (um repositório git)
**Decisão:** todo o sistema num único repo (§2). **Por quê:** desenvolvedor solo + IA construtora; o `core_domain`/contratos compartilhados exigem refatoração atômica entre produtor e consumidores no mesmo commit; polyrepo só compensa com times autônomos e ciclos de release independentes — não é o caso. **Reconsiderar quando:** existirem times de engenharia separados que precisem de release independente.

### ADR-002 — Serviços separados por PERFIL técnico, não por agente
**Decisão:** 5 Cloud Run (`svc-agents`, `svc-render`, `svc-publisher`, `svc-cockpit-api`, `svc-cost-guardian`), mas TODOS os agentes co-localizados em `svc-agents` — **não** um Cloud Run por agente (§1). **Por quê:** a separação dos 5 segue diferença real de recurso/escala/IAM (render = CPU pesada/escala-a-zero; publisher = credenciais sensíveis/janelas; guardian = leve/crítico). Um serviço por agente traria 12+ cold starts, latência de rede em cada handoff (o planejamento encadeia 5 agentes), e 12 deploys — custo de microserviço para uma escala de dezenas de itens/dia, sem o problema que microserviço resolve. Handoffs como chamada de função, não de rede. **Reconsiderar quando:** um agente precisar de recurso próprio (ex.: Editor de vídeo com GPU) ou de escala independente — extrair é barato porque o handoff já é o contrato `AgentRequest`/`AgentResponse`, idêntico em memória ou via Pub/Sub. A fronteira de extração natural é **por time/domínio** (campo `team` do `PlatformAgent`), não por agente individual.

### ADR-003 — Monolito modular agora, costuras para virar serviços depois
**Decisão:** os contratos (§4, §8) serializam igual em memória e via Pub/Sub, permitindo extração futura sem reescrever consumidores. **Por quê:** evita complexidade distribuída prematura (consistência eventual, debug entre serviços) antes de existir o problema de escala. **Reconsiderar quando:** a dor de escala/acoplamento aparecer de fato — e aí extrair pela costura já existente.
