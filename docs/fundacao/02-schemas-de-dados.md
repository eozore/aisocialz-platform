# 02 — Schemas de Dados (Firestore)

Convenções: snake_case; timestamps ISO-8601 UTC; todo documento tem `created_at`, `updated_at`. Campos `[PREENCHER]` exigem input do Victor.

> **Escopo multi-tenant (doc 09 §2):** todas as collections abaixo vivem sob `tenant/{tenant_id}/brands/{brand_id}/...`, exceto as globais sob `platform/`. Na V1 há um único tenant (Victor), mas **toda query carrega `tenant_id` + `brand_id`** — nunca assumir "a marca". As collections de tenant são por-marca salvo indicação.

## Collections

```
# Por marca: tenant/{tid}/brands/{bid}/...
strategies/{bid}/versions/{vN}         # estratégia versionada
backlog/{item_id}                      # unidade de trabalho
content_graph/{content_id}             # memória institucional (+ template_id, assets_usados)
learnings/{learning_id}                # knowledge base do Analista
decision_log/{decision_id}             # decisões humanas e do Diretor
agent_memory/{agent_id}/notes/{note}   # caderno próprio de cada agente
schedule/{slot_id}                     # calendário
publications/{idempotency_key}         # registro de publicação
community_interactions/{interacao_id}  # comentários/menções + score (doc 08 §1)
crisis_events/{evento_id}              # eventos de crise + severidade (doc 08 §2)
media_assets/{asset_id}                # acervo de mídia vetorizado (doc 10 §4)
templates/{template_id}                # templates aprovados da marca (doc 07, doc 10)

# Por tenant: tenant/{tid}/...
brands/{bid}                           # invariantes da marca (doc 04)
team_subscriptions                     # times contratados/ativos (doc 09 §3)
cost_ledger/{entry_id}                 # custo (doc 05), rateável por marca
config                                 # flags do tenant (status, modo, orçamento)
approvals/{approval_id}                # fila do CEO

# Global: platform/...
marketing_kb/{doc_id}                  # KB universal de marketing (doc 09 §4)
format_catalog/{format_id}             # formatos + templates-base (doc 10 §2)
pricing, model_routing                 # tabela de custos e routing de modelos
```

## strategies/{brand}/versions/{vN}

```json
{
  "version": "v1-2026Q2",
  "status": "ativa",
  "objetivo": "construir autoridade e audiência em transição de carreira para dados/IA",
  "tese_central": "qualquer profissional disciplinado consegue migrar para dados/IA com fundamentos sólidos e portfólio real",
  "persona_primaria": {
    "quem": "profissional CLT, 25-40, querendo migrar para dados/IA",
    "dores": ["por onde começar", "matemática assusta", "síndrome de impostor", "pouco tempo livre"],
    "nivel": "iniciante com noção de negócio",
    "onde_esta": ["instagram", "youtube", "linkedin"]
  },
  "personas_secundarias": ["gestores avaliando adoção de IA", "devs migrando para ML"],
  "funil": {
    "topo":  {"formatos": ["reel", "thread", "carrossel"], "objetivo": "alcance e identificação"},
    "meio":  {"formatos": ["youtube_longo", "blog", "newsletter"], "objetivo": "profundidade e confiança"},
    "fundo": {"formatos": ["serie/trilha", "cta_crescimento"], "objetivo": "conversão de audiência: seguir/inscrever"}
  },
  "objetivo_de_conversao": {
    "tipo": "audiencia",
    "metrica_primaria": "novos_seguidores + novos_inscritos_youtube",
    "nota": "fase inicial: meta é CRESCER audiência, não vender. Quando houver produto (mentoria/curso), trocar tipo para 'receita' sem mexer no resto."
  },
  "pilares": [
    {"nome": "fundamentos sem medo", "peso": 0.4, "exemplos": ["estatística", "variáveis aleatórias", "python", "ML básico"]},
    {"nome": "carreira e mercado", "peso": 0.3, "exemplos": ["vagas", "portfólio", "entrevistas", "salários"]},
    {"nome": "ia aplicada a negócios", "peso": 0.2, "exemplos": ["casos reais", "governança", "cloud"]},
    {"nome": "bastidores e opinião", "peso": 0.1, "exemplos": ["rotina", "erros", "hot takes com dados"]}
  ],
  "metas_trimestre": [{"metrica": "[PREENCHER]", "alvo": "[PREENCHER]"}],
  "changelog": "primeira versão da estratégia de transição de carreira"
}
```

**Regra:** agentes leem sempre a versão `status: ativa` em runtime. Trocar de público = criar `vN+1` e ativar. O Analista mantém comparativos entre versões.

## backlog/{item_id}

```json
{
  "brand": "eozore",
  "tipo": "carrossel | post_linkedin | thread | youtube_longo | reel_gravado | reel_renderizado | blog | newsletter_item | corte_short | card_noticia",
  "pilar": "fundamentos sem medo",
  "funil": "topo",
  "fonte": {"tipo": "pauta | video | noticia_ainewz", "ref": "content_atom_id | noticia_id"},
  "requer_ceo": false,
  "status": "ideia | briefing | producao | revisao | aguardando_ceo | aprovado | agendado | publicado | rejeitado",
  "slot_alvo": "slot_id",
  "experimento": {"ativo": false, "hipotese": null, "variante": null},
  "referencias_grafo": ["yt-2026-04-variaveis-aleatorias"],
  "artefatos": {"texto": "gs://...", "imagens": ["gs://..."], "video": "gs://..."},
  "historico": [{"agente": "redator", "acao": "draft_v1", "custo_brl": 0.12, "ts": "..."}]
}
```

## content_graph/{content_id}

```json
{
  "brand": "eozore",
  "titulo": "Variáveis aleatórias sem medo",
  "conceitos": ["variáveis aleatórias", "distribuições", "probabilidade"],
  "depende_de": ["probabilidade básica"],
  "prerequisito_de": [],
  "pilar": "fundamentos sem medo",
  "funil": "meio",
  "formato": "youtube_longo",
  "canal": "youtube",
  "url": "https://youtu.be/XXXX",
  "como_referenciar": {
    "youtube": "link com timestamp na descrição",
    "linkedin": "link no primeiro comentário",
    "instagram": "'busca <título curto> no canal' + link na bio"
  },
  "publicado_em": "2026-04-12",
  "performance": {"views": 0, "retencao_pct": 0, "ctr": 0, "saves": 0, "atualizado_em": "..."},
  "embedding": [/* vetor — Firestore vector field */]
}
```

**Regras do grafo:**
1. O Publicador cria/atualiza o nó no momento da publicação (com URL real). O Analista atualiza `performance` diariamente.
2. Antes de produzir, Redator/Roteirista fazem retrieval (top-k vetorial + match de `conceitos`) e recebem os nós relevantes no contexto. Se o conteúdo novo assume um conceito coberto antes, a referência acionável é **obrigatória** no formato nativo do canal (`como_referenciar`). O Revisor reprova peça que cita "já falei disso" sem caminho concreto de acesso.
3. **Detecção de lacunas:** job semanal varre `depende_de` apontando para conceitos sem nó publicado → vira sugestão de pauta para o Estrategista.
4. **Trilhas retroativas:** o Estrategista pode encadear nós existentes em séries (fundo de funil).
5. Backfill inicial: indexar todo o conteúdo já publicado do Victor e do AINewz (doc 06, fase 1).

## learnings/{learning_id}

```json
{
  "brand": "eozore",
  "aprendizado": "carrossel técnico com gancho de pergunta performa 2.1x às terças 12h",
  "dimensoes": {"formato": "carrossel", "gancho": "pergunta", "dia": "ter", "hora": "12:00", "pilar": "fundamentos sem medo"},
  "evidencia": ["post-031", "post-047", "post-052"],
  "n_amostras": 3,
  "confianca": 0.7,
  "status": "hipotese | em_teste | promovido | descartado | expirado",
  "acao_recomendada": "estrategista prioriza esse slot para o pilar",
  "auto_aplicavel": true,
  "validade": "2026-09-01"
}
```

`auto_aplicavel: true` apenas para micro-otimizações (horário, frequência, formato de gancho). Mudanças de estratégia → vira recomendação no relatório semanal, nunca auto-aplica. Aprendizados com `n_amostras < 3` não saem de `hipotese`. Tudo tem `validade` — o Diretor expira na retro.

## decision_log/{decision_id}

```json
{
  "quem": "victor | diretor",
  "contexto": "planejamento semanal 2026-06-07",
  "decisao": "priorizar carrosséis sobre reels por 4 semanas",
  "racional": "hipótese de maior salvamento no público iniciante",
  "alternativas_rejeitadas": ["manter mix atual"],
  "resultado_observado": null,
  "revisar_em": "2026-07-05"
}
```

Usado pelos agentes para discordar com memória ("em março decidimos X e o alcance caiu 30%"). O Analista preenche `resultado_observado` na data de revisão.

## agent_memory/{agent_id}/notes/{note_id}

```json
{
  "tipo": "retro | playbook | preferencia_do_ceo",
  "conteudo": "markdown curto e declarativo",
  "origem": "retro semanal 2026-06-05",
  "curado_pelo_diretor": true,
  "expira_em": "2026-12-01"
}
```

Higiene: na retro de sexta o Diretor consolida (merge de notas redundantes, remoção de contradições — a mais recente com evidência vence), descarta notas não-curadas há 30 dias e lista no relatório semanal toda mudança de "crença" relevante. Memórias são markdown legível — o Victor audita a cabeça da equipe.

## schedule/{slot_id} e approvals/{approval_id}

```json
// slot
{"brand": "eozore", "canal": "instagram", "dia": "2026-06-16", "hora": "12:00",
 "pilar": "fundamentos sem medo", "funil": "topo", "item": "item_id | null",
 "origem_hora": "learning-0042 | default", "status": "vago | reservado | publicado"}

// approval
{"tipo": "roteiro | item | estrategia | aprendizado_macro", "ref": "item_id",
 "resumo_para_decisao": "3 linhas + link preview", "prazo": "...",
 "fallback_sem_resposta": "aplicar | segurar", "resposta": null, "motivo": null}
```
