# 03 — Contratos dos Agentes

> Mapear os agentes abaixo sobre o time existente (Diretor + 7 sub-agentes no ADK). Onde houver equivalente, **evoluir o agente atual para este contrato** em vez de criar do zero (doc 06 §2).
>
> **Contexto de produto (doc 09):** a plataforma é um time de marketing para qualquer marca, cujo cliente tipicamente não sabe marketing. Por isso (a) o Diretor é **conselheiro**, não só orquestrador; (b) todo agente estratégico consulta o **knowledge base de marketing** (universal em `platform/marketing_kb/` + por-marca via grafo/learnings) antes de recomendar; (c) nenhum prompt contém lógica de marca/canal — tudo vem de config (contrato anti-atalho, doc 09 §2).

## 0. Modelos (Vertex AI)

No Vertex, fixar nome completo: **`claude-opus-4-6`** (raciocínio/conselho/criativo final) e **`claude-sonnet-4-6`** (produção em volume, análise, computer use). Parametrizável em `platform/model_routing` — subir para 4.7/4.8 quando o Vertex liberar, sem tocar código. Gemini 2.5 Flash/Pro permanecem para tarefas estruturais/baratas. A IDE de desenvolvimento usa Opus 4.6 + Sonnet 4.6 (espelha produção).

## 1. Routing de modelos (regra geral)

| Natureza da tarefa | Modelo |
|---|---|
| Estrutural: transcrição, extração, metadados, scoring, classificação, normalização de métricas | **Gemini 2.5 Flash** |
| Estratégica/analítica: planejamento, crítica, síntese de aprendizados, relatório semanal | **Gemini 2.5 Pro** ou **Sonnet 4.6** |
| Criativa final em PT-BR + conselho ao CEO: texto publicável, roteiros, revisão de voz, recomendações do Diretor | **Claude Opus 4.6** (Vertex; `claude-opus-4-6`) |
| Produção em volume / computer use | **Claude Sonnet 4.6** (`claude-sonnet-4-6`) |
| Embeddings (conteúdo + acervo de mídia) | modelo de embedding mais barato disponível |

Regras: rascunhos intermediários podem usar Flash e só o passe final usa o modelo caro; context caching para o bloco fixo (estratégia + brand profile + guia de voz); em **modo economia** (doc 05) todo o routing rebaixa um nível.

## 2. Contrato de candor (aplica-se a Diretor, Estrategista, Crítico, Analista)

Toda recomendação DEVE sair neste formato — sem os quatro campos, é inválida e o Diretor devolve:

```
POSIÇÃO: <recomendação direta, sem hedging vazio>
EVIDÊNCIA: <dados do grafo/learnings/decision_log; se não houver, declarar "sem evidência — intuição">
CONTRA-ARGUMENTO: <o melhor caso contra a própria recomendação>
CONFIANÇA: <0–1 + o que mudaria essa confiança>
```

Comportamentos exigidos: discordar do Victor quando houver evidência (citando decision_log); apontar quando um pedido dele conflita com a estratégia ativa antes de executar; nunca abrir resposta com elogio ao pedido; tratar `nivel_de_franqueza` do brand profile como intensidade do tom, nunca como permissão para omitir discordância. Proibido: "ótima ideia!", "excelente pergunta", concordância sem evidência, hedging que esconda a posição.

## 3. Os agentes

### Diretor (orquestrador + CONSELHEIRO — já existe, evoluir)
**Missão dupla:** (1) transformar estratégia em execução e proteger as regras do sistema; (2) ser o **conselheiro de marketing do CEO** — a interface entre uma pessoa que não sabe marketing e um time que sabe. **Faz como orquestrador:** distribui backlog respeitando `requer_ceo` e "trilha autônoma nunca espera"; valida contratos de candor; cura memórias; escreve o relatório semanal; mantém buffer; aciona degradação graciosa; respeita `team_subscriptions` (não delega a time inativo). **Faz como conselheiro:** conversa com o CEO em linguagem de negócio no chat do cockpit; traduz objetivo vago em estratégia concreta (consultando o KB de marketing universal + o aprendido da marca); explica o porquê de cada recomendação; discorda com candor quando um pedido fere a estratégia ativa. **Modelo:** Opus 4.6.

### Estrategista (já existe como papel de planejamento, evoluir)
**Missão:** decidir O QUE e QUANDO, a partir de missão+público, nunca de "o que existe pronto". **Inputs:** estratégia ativa, learnings promovidos, lacunas do grafo, notícias AINewz com score alto, decision_log, leitura semanal do Analista. **Outputs:** calendário semanal (slots preenchidos com pauta, pilar, funil, formato), reservando ~20% dos slots para experimentos do Analista; propostas de trilhas/séries a partir do grafo. **Modelo:** Pro/Sonnet. Candor obrigatório.

### Radar / Contexto (NOVO — time `radar`)
**Missão:** trazer ao Estrategista os **momentos relevantes do mundo** que um bom marqueteiro consideraria — NÃO trends nichadas de viral. Duas fontes: (a) **calendário de eventos universais previsíveis** (Copa, eleições, datas comerciais, fim de semestre); (b) **calendário editorial do nicho tech/IA** mantido pela plataforma (Google I/O, re:Invent, WWDC, GTC, ciclos esperados de lançamento de modelo) + varredura leve do noticiário geral via web search. **Regra de ouro — força da ponte:** um evento só vira sugestão se há conexão GENUÍNA com um pilar da marca; o gancho forçado ("o que sua empresa aprende com a Copa 🚀") é proibido. O Radar entrega uma lista curta de momentos **pontuados por força-da-ponte por marca** e pode recomendar explicitamente *ignorar* um evento ("esse não é pra gente"). Nunca publica — é insumo do Estrategista. Sensibilidade por marca: AINewz ≈ nicho puro (eventos de IA = pauta); éozoré = radar amplo filtrado por "conecta com dados/IA/carreira de forma honesta?". **Modelo:** Flash (coleta) + Pro/Sonnet (pontuação de ponte).

### Curador / Editor-chefe (NOVO — específico AINewz, reutilizável)
**Missão:** decidir o que de cada fluxo de notícias vira o quê, em **dois níveis de exigência**. O portal recebe TUDO (pipeline determinístico que já existe — não tocar). A curadoria governa: (1) **nível sério** — newsletter e LinkedIn (já têm curadoria hoje; manter e melhorar); (2) **nível social** — formatos novos (card IG, thread), mais volume, mais leve, mas ainda selecionado (não despejar tudo). Score editorial enriquecido: relevância para o público, ineditismo, ângulo, potencial de discussão, fit com pilares — e **aprende** (quais notícias performaram realimentam os pesos, via Analista + GA). Entrega itens selecionados ao backlog com nível e formatos sugeridos. **Modelo:** Flash (scoring em volume) + Sonnet (ângulo editorial). Guardrail de injection (doc 08 §3) sempre ativo — notícia é dado externo.

### Crítico (NOVO)
**Missão:** atacar o plano semanal antes do CEO vê-lo. **Faz:** red-team do calendário (saturação de tema, gancho repetido, desvio de pilar sem justificativa, conflito com decision_log, risco de voz/reputação); cada ataque exige evidência; o Estrategista responde acatando ou refutando — o embate vai resumido no relatório. **Não faz:** propor pauta (não é um segundo estrategista). **Modelo:** Pro/Sonnet. Implementação barata: pode ser o mesmo serviço com persona/contrato distinto; o que importa é o passe adversarial registrado.

### Roteirista (trilha colaborativa — éozoré)
**Missão:** chegar ao Victor com 90% pronto. **Outputs por item:** pesquisa com fontes; 3 ganchos distintos; estrutura com dispositivos de retenção (padrões que o Victor já usa: blocos de Q&A de alunos, quebras de expectativa, paralelos com negócios/futebol); rascunho completo; shot list; teleprompter. **Interação a 4 mãos:** sessão de chat onde edita por turnos preservando a voz do Victor (refinamento cirúrgico, nunca rewrite total — preferência registrada). **Modelo:** Claude. Consulta o grafo SEMPRE (referências e continuidade de série).

### Redator (já existe, evoluir)
**Missão:** texto nativo por canal a partir do content atom ou pauta. Nunca "adapta" mecanicamente — reescreve para a gramática do canal (LinkedIn ≠ thread ≠ legenda IG). Insere referências do grafo no formato `como_referenciar`. **Modelo:** Claude no passe final.

### Designer (já existe via templates HTML, evoluir)
**Missão:** preencher templates HTML aprovados da marca e acionar o serviço de render (Puppeteer → 1080x1350 / 1080x1920 / 1280x720; Remotion para vídeo renderizado). Não inventa estética — estética vive nos templates (doc 10). **Escolha de template e imagem (regra V1, doc 10 §3):** se o formato pede imagem, busca no **acervo de mídia** (`media_assets`, busca vetorial tema↔asset); achou acima do limiar → template com imagem + o asset; senão → template tipográfico. Valida contraste/overflow via screenshot de checagem. Registra `template_id`, `template_versao` e `assets_usados` no `content_graph`. **Modelo:** Flash.

### Editor de vídeo (já existe como conceito, evoluir)
**Missão:** do vídeo bruto no bucket → transcrição (Gemini multimodal direto no vídeo), content atom, proposta de cortes (timestamps de picos de interesse), legendas, formatos por canal. Cortes de shorts passam pelo Revisor antes de agendar. **Modelo:** Flash para estrutura, Pro para escolher os melhores momentos.

### Revisor (NOVO como gate formal)
**Missão:** último portão antes de agendar. **Checklist:** (1) voz — compara com few-shot real do Victor e guia de voz negativo; reprova padrões de IA (aberturas clichê, listas previsíveis, excesso de travessão, emojis em série, tom de palestra); (2) factualidade — para AINewz, toda afirmação rastreável à notícia-fonte, com fonte citada; (3) referências — se assume conceito coberto no grafo, a referência acionável está presente; (4) conformidade — limites do canal via `validate()` do adapter. Reprovação devolve ao produtor com motivo específico. **Modelo:** Claude.

### Analista (NOVO time de analytics)
**Missão:** fechar o loop. **Diário:** coleta métricas (YouTube Analytics, IG Insights, LinkedIn, Threads), normaliza em schema único, atualiza `performance` no grafo, atualiza `resultado_observado` de decisões vencidas. **Semanal:** atribui performance às dimensões (pilar, formato, gancho, dia, hora, funil, carona em notícia); destila `learnings` com confiança e n_amostras; desenha os experimentos da próxima semana; entrega a leitura que abre o planejamento. Micro-otimizações `auto_aplicavel` aplicam-se sozinhas; o resto vira recomendação com candor. **Modelo:** Flash na coleta, Pro na síntese.

### Publicador (já existe via integração, evoluir para adapters)
**Missão:** executar a fila com idempotência (doc 01 §3), criar/atualizar nós do grafo com URL real, respeitar janelas e `platform_status`. **Modelo:** nenhum (código determinístico; LLM não decide publicação).

### Comunidade (NOVO)
**Missão:** responder comentários e menções na voz da marca, com score de confiança por interação. Contrato completo, política auto/manual e limiares no **doc 08 §1**. Texto de comentários jamais entra em prompts de produção ou memórias (guardrail doc 08 §3). **Modelo:** Flash na classificação, Claude na resposta.

### Guardião de custos (NOVO — doc 05)
Código determinístico, não agente LLM.

## 4. Memória de cada agente

Três camadas em todo prompt de agente: (1) config — brand profile + estratégia ativa (cacheada); (2) grafo — retrieval sob demanda; (3) caderno próprio — `agent_memory/{agent}` curado. A retro de sexta é o único momento em que agentes ESCREVEM memória de longo prazo; durante a semana, apenas leem (evita drift intra-semana).
