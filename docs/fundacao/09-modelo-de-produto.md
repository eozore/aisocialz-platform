# 09 — Modelo de Produto (multi-tenant, times contratáveis)

> Este documento reorienta o pacote: a plataforma deixa de ser "a equipe do Victor" e passa a ser **um produto de marketing orgânico operado por IA, aplicável a qualquer marca**. O Victor é o primeiro cliente (marcas éozoré e AINewz). O objetivo de longo prazo é abrir como SaaS, onde donos de marca — que tipicamente **não sabem marketing** — contratam um time de IA que planeja, produz, publica, mede e os aconselha.
>
> Em caso de conflito, a ordem de precedência é: doc 09 → doc 08 → demais.

## 1. A tese do produto

O valor vendido não é "IA que posta". É **"IA que sabe marketing e te conduz"**. O cliente típico não sabe o que postar, quando, em que formato, nem por quê. A plataforma entrega a competência de um time de marketing inteiro — incluindo a função de **conselheiro** que traduz objetivo de negócio vago ("quero virar referência em X") em estratégia executável e explica o porquê de cada recomendação.

Três implicações que atravessam toda a arquitetura:

1. **Knowledge base de marketing é ativo de primeira classe** (doc 03 §0 e abaixo §4). Os agentes não dependem só do que o modelo sabe genericamente; operam sobre uma base curada de princípios de marketing — universal (do produto) + aprendida por marca (grafo + learnings).
2. **O Diretor é conselheiro, não só orquestrador** (doc 03). Ele conversa com o CEO em linguagem de negócio, recomenda com candor, e discorda quando o pedido fere a estratégia.
3. **Transparência é feature.** O cliente precisa VER o time trabalhando para confiar e para justificar a assinatura (doc 09 §5).

## 2. Multi-tenancy com fronteiras limpas (o contrato anti-atalho)

A V1 roda para um usuário (Victor) com múltiplas marcas, mas é construída para virar multi-tenant **sem reescrever o miolo**. A regra inviolável que garante isso:

> **Nenhuma lógica de marca, de usuário ou de canal vive em código ou em prompt de agente. Tudo que é específico vive em configuração (brand profile, estratégia, KB, catálogo, acervo). O código e os prompts só conhecem "uma marca qualquer", "um canal qualquer", "um tenant qualquer".**

Hierarquia de dados (toda collection do doc 02 ganha o prefixo de escopo):

```
tenant/{tenant_id}                      # conta (V1: um único tenant = Victor)
  brands/{brand_id}                     # marcas do tenant (eozore, ainewz)
    strategies/, content_graph/, learnings/, backlog/, schedule/,
    media_assets/, publications/, community_interactions/, crisis_events/
  cost_ledger/                          # custo por tenant (rateável por marca)
  team_subscriptions/                   # quais times estão "contratados" (§3)
  config                                # flags do tenant
platform/                               # GLOBAL, compartilhado entre tenants
  marketing_kb/                         # KB universal de marketing (§4)
  format_catalog/                       # formatos + templates-base (doc 10)
  pricing/, model_routing/
```

O que isso exige da construtora na V1 (barato agora, evita reescrita depois):
- Toda query carrega `tenant_id` + `brand_id`. Mesmo com um tenant só, **nunca** assumir "a marca" — sempre resolver pela config.
- Recursos globais (`platform/`) separados de recursos de tenant desde o dia 1.
- Isolamento real só na virada SaaS (regras de segurança Firestore por tenant, billing por conta); na V1 basta a disciplina de escopo.

## 3. Times como módulos contratáveis

Cada **time** é um módulo plugável: um pacote de (agentes + adapters + templates + KB específico + telas). O CEO ativa só os times que usa. Quem não faz TikTok não ativa o time de TikTok; quem não tem newsletter não ativa o de newsletter.

```json
// tenant/{id}/team_subscriptions
{
  "core":        {"ativo": true,  "obrigatorio": true},   // Diretor, Estrategista, Crítico, Revisor, Analista — base sempre on
  "linkedin":    {"ativo": true},
  "meta":        {"ativo": true},   // Instagram + Facebook + Threads
  "blog":        {"ativo": true},
  "radar":       {"ativo": true},   // agente de Contexto (doc 03)
  "comunidade":  {"ativo": true},
  "youtube":     {"ativo": false},  // Fase 2
  "tiktok":      {"ativo": false},  // Fase 2
  "analytics_web": {"ativo": true}, // Google Analytics — Fase 1 (ver doc 06)
  "email":       {"ativo": false},  // Fase 2
  "video_ia":    {"ativo": false}   // futuro: edição de vídeo por IA (§6)
}
```

Dois significados do mesmo mecanismo (padrão recorrente da plataforma, como auto/manual):
- **Uso pessoal (Victor):** "contratar" = ativar o módulo. Sem cobrança.
- **SaaS futuro:** "contratar" = item de assinatura. Ativar custa. Billing por time ativo + consumo.

Implicação arquitetural que a construtora deve respeitar na V1: cada time é **independente e desativável**. Desligar `tiktok` não pode quebrar nada; o Scheduler, o Estrategista e o cockpit checam `team_subscriptions` antes de agir sobre um canal. Um time inativo é invisível — não gera slots, não aparece no cockpit, não consome.

## 4. Knowledge base de marketing (V1: simples)

Duas camadas:

- **Universal** (`platform/marketing_kb/`) — princípios que valem para qualquer marca: frameworks de funil, anatomia de bons ganchos, princípios por canal, o que é AIDA/jobs-to-be-done, boas práticas de carrossel/thread/post. **V1: começar enxuto** — alguns documentos markdown curados, consultáveis por retrieval. Cresce com o tempo; é ativo do produto.
- **Por marca** — já existe no pacote: `content_graph` (memória do que foi feito) + `learnings` (o que funcionou). É o que o produto "aprende" sobre cada cliente.

O Diretor-conselheiro e o Estrategista consultam ambas antes de recomendar. Na V1, o KB universal é injetado como contexto; não há ainda curadoria automática dele (isso é evolução).

## 5. Cockpit como produto: visualização de processo

Além de fila/calendário/relatório (doc 00 §5), o cockpit ganha **visibilidade do pipeline ao vivo** — porque o cliente precisa ver o time trabalhando:

- **Esteira de produção:** cada item do backlog mostra em que etapa está e qual agente o segura (ex.: notícia → Curador pontuou 0.8 → Redator escrevendo → aguardando Revisor). Transparência vira confiança.
- **Sala de contratação:** as telas de ativar/desativar times (§3). No SaaS, é a tela de planos.
- **Conversa com o Diretor:** canal de chat onde o CEO fala em linguagem de negócio e o Diretor aconselha, explica decisões e recebe diretrizes.
- Mantidos do doc 00: fila de aprovações, calendário, relatório semanal, controles (autonomia, franqueza, modo férias, orçamento), widget de custo (doc 05).

**V1 do cockpit:** esteira (read-only), fila de aprovações, calendário, sala de contratação básica (toggles), chat com Diretor. O resto evolui.

## 6. Vídeo: o que entra quando

- **Fase 1 e 2:** vídeo automatizado = apenas **motion/render** (Remotion, "carrossel em movimento", cards animados). Vídeos gravados (longos e cortes) são **manuais, feitos pelo Victor**.
- **Futuro (`video_ia`):** time de edição de vídeo por IA que pega gravações brutas do Victor, edita, e disponibiliza num **repositório de vídeos editados** de onde o time de publicação consome formatos prontos. Previsto, não construído. A arquitetura deve deixar o "repositório de mídia editada" como um tipo de fonte do acervo (doc 10), para plugar depois sem redesenho.

## 7. Faseamento (substitui o do doc 06 §3)

**Fase 1 — Profundidade nos canais com API + medição.** LinkedIn, Meta (Instagram/Facebook/Threads) e Blog funcionando bem em **todos os formatos**, com Google Analytics desde já fechando o funil até os sites. Inclui: core de agentes, Diretor-conselheiro, Radar, Curador do AINewz, grafo+learnings, acervo de mídia (doc 10), catálogo de formatos com templates-base, Revisor, Comunidade, FinOps, cockpit V1. As duas marcas em sandbox → produção canal a canal.

**Fase 2 — Expansão.** YouTube + TikTok (canais de vídeo; cortes manuais do Victor + motion) + Email (relacionamento com seguidores; reabre desenho de consentimento/LGPD — ver nota abaixo). 

**Futuro (sem fase):** SaaS (auth multi-tenant, onboarding self-service, billing por assinatura), `video_ia`, verificação automática de direitos de imagem (doc 10 §4), curadoria automática do KB universal, WhatsApp.

> Nota Email/relacionamento (Fase 2): publicar (broadcast) ≠ relacionar (bidirecional, consentido). Email exige opt-in/LGPD, gestão de lista e voz mais sensível. Tratar como desenho próprio quando chegar, não como "mais um adapter".

## 8. Conexão de contas e credenciais (peça de produto)

Cada canal exige credenciais da marca (tokens OAuth, chaves de API). Hoje (V1, só o Victor) elas são populadas à mão no Secret Manager; como produto, **cada CEO conecta as próprias contas**. A estrutura nasce multi-tenant desde já (anti-atalho).

**Fluxo (produto):** na sala de contratação, ao ativar um time de canal, o CEO vê "Conectar conta do {canal}". Onde houver OAuth (LinkedIn, Meta, Google/YouTube, TikTok), é um fluxo de autorização → a plataforma recebe e guarda o token; onde não houver, cola-se a chave manualmente. O token é gravado no Secret Manager sob caminho **escopado por tenant**:

```
secret: {tenant_id}--{brand_id}--{canal}--credentials   # isolado por tenant
```

**Regras inegociáveis:**
- Credencial do tenant A é fisicamente inacessível ao tenant B (caminho escopado + IAM por tenant na virada SaaS). Mesmo princípio do Firestore (doc 09 §2).
- Só o `svc-publisher` lê esses secrets, em runtime (doc 01 §4). Nenhum agente, nenhum prompt, nunca o cockpit.
- **Refresh automático:** tokens de vida curta (notadamente Meta — Instagram, Facebook, **Threads** — expiram em ~60 dias) são renovados programaticamente pelo job diário de saúde de credenciais (doc 08 §5). Falha no refresh → canal entra em hold + alerta com link de reconexão (1-2 cliques), nunca falha silenciosa.
- **Status visível no cockpit:** cada canal mostra conectado / expira em N dias / desconectado. Reconexão é self-service.

**V1 vs SaaS:** na V1 o Victor popula uma vez (pode ser manual via console). Mas o *nome e o escopo* dos secrets já seguem o padrão acima — assim a virada SaaS é adicionar o fluxo OAuth no cockpit, não refatorar onde as chaves vivem.
