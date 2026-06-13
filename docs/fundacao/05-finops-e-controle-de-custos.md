# 05 — FinOps e Controle de Custos

Orçamento mensal de referência: **R$600**, com três gatilhos. Premissa de projeto: **billing do GCP atrasa horas** — por isso o controle tem duas camadas: o ledger interno (tempo quase real, enforcement) e o Cloud Billing Budget (verdade contábil, rede de segurança).

## 1. Os três gatilhos

| Acumulado no mês | Modo | O que acontece |
|---|---|---|
| **R$200** | `aviso` | Notificação ao Victor com breakdown (por agente, marca, modelo, serviço) + projeção de fim de mês. Nenhuma mudança operacional. |
| **R$400** | `economia` | Automático: routing de modelos rebaixa um nível (Pro→Flash; Claude só no passe final de peças já em produção); experimentos pausados; frequência de produção reduzida a 60% dos slots (prioriza pilares de maior peso); render de vídeo (Remotion) suspenso, só imagens; AINewz reduz `top_n_dia` para 1. Publicação do buffer continua (custo ~zero). Notificação com o que foi cortado. |
| **R$600** | `bloqueado` | Automático: `platform_status: paused` — todo Cloud Scheduler job e todo agente checam essa flag e abortam; única operação viva: publicar buffer já pronto e aprovado + alertas. Sair do bloqueio exige ação explícita do Victor no cockpit (aumentar orçamento do mês ou aceitar parada até o dia 1). |

Os valores são configuração em `platform/config.budget`, não constantes no código:

```json
{
  "budget": {
    "mensal_brl": 600,
    "gatilhos": [
      {"valor": 200, "modo": "aviso"},
      {"valor": 400, "modo": "economia"},
      {"valor": 600, "modo": "bloqueado"}
    ],
    "moeda_billing": "USD",
    "cambio_referencia": "atualizar 1x/dia via API de cotação; usar margem de 5% a favor do bloqueio"
  },
  "platform_status": "ativo | economia | paused",
  "gasto_mes_ledger_brl": 0
}
```

## 2. Camada 1 — Ledger interno (enforcement em tempo quase real)

Toda chamada custosa registra em `cost_ledger/`:

```json
{
  "ts": "...", "brand": "eozore", "agente": "redator", "item": "item_id",
  "conta": "operacao",   // "operacao" | "build" — APENAS "operacao" conta para os gatilhos (doc 08 §7)
  "servico": "vertex_llm | vertex_embedding | cloud_run_render | storage | outro",
  "modelo": "claude-x | gemini-2.5-flash | ...",
  "tokens_in": 3200, "tokens_out": 980,
  "custo_estimado_brl": 0.14
}
```

Implementação: wrapper único de chamadas LLM (todo agente passa por ele — proibido chamar Vertex direto) que (a) calcula custo por tabela de preços versionada em `platform/pricing`, (b) grava o entry, (c) incrementa `gasto_mes_ledger_brl` (transação/sharded counter), e (d) **antes** da chamada, checa o modo vigente e aplica o routing correspondente. O guardião (Cloud Function leve, acionada por trigger no contador ou a cada 10 min) compara o acumulado com os gatilhos e troca o modo. Render no Cloud Run loga custo estimado por job (vCPU·s × preço).

Orçamentos secundários (defesa em profundidade): teto diário por marca (`R$ mensal / 30 × 1.5`) e teto por item (`R$2` default) — estourou, item pausa e vira alerta, evitando loop de retry queimando orçamento.

## 3. Camada 2 — Cloud Billing Budget (verdade contábil)

Criar um Budget no projeto com valor mensal equivalente a R$600 (em USD pela referência de câmbio), thresholds em 33% / 66% / 100%, publicando em `custo-alerta` (Pub/Sub). A mesma função guardiã consome e:

- Se o billing real indicar gatilho que o ledger ainda não atingiu → **o billing vence** (significa custo fora do ledger: storage, rede, serviço esquecido). Aplica o modo e abre alerta de investigação "custo não rastreado".
- Reconciliação semanal: ledger vs billing real; divergência > 15% vira tarefa de correção da tabela de preços/instrumentação no relatório do CEO.

Importante: budget do GCP **não bloqueia gasto nativamente** — o bloqueio é nosso (flag + checagem obrigatória). Não usar desativação de billing do projeto (derruba tudo, inclusive o cockpit e os alertas).

## 4. Engenharia de custo (decisões de projeto)

1. **Routing por natureza da tarefa** (doc 03 §1) — a maior alavanca.
2. **Context caching** do bloco fixo (estratégia + profile + guia de voz) em toda chamada repetitiva.
3. **Rascunho barato, passe final caro**: Flash gera, Claude/Pro refina uma vez. Nunca iterar N vezes no modelo caro.
4. **Batch onde não há urgência**: análise diária de métricas e embeddings em lote.
5. **Retries com teto** (máx 3) e teto de custo por item.
6. **Render sob demanda** com `min-instances=0`; Remotion só para formatos que comprovadamente performam (decisão do Analista, não default).
7. **Firestore vector search no MVP** (sem custo fixo de índice do Vector Search até a escala justificar).
8. Relatório semanal sempre inclui: custo por peça publicada, por marca e por agente — "custo por conteúdo" é métrica de primeira classe ao lado de performance.

## 5. Visibilidade no cockpit

Widget permanente: gasto do mês (ledger) vs orçamento, barra com os três gatilhos, projeção de fim de mês, top 5 consumidores. Modo vigente sempre visível. Trocar de modo manualmente é permitido ao Victor a qualquer momento.
