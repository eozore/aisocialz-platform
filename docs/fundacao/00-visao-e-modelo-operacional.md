# 00 — Visão e Modelo Operacional

> **Para a IA construtora:** este pacote (documentos 00–10) é a especificação fundacional da plataforma. Ele NÃO substitui o projeto em andamento (Diretor + sub-agentes em Google ADK) — ele o turbina. Leia todos antes de alterar qualquer código. Ponto de entrada: **doc 06** (integração e fases). Precedência em conflito: **doc 09 (produto) → doc 08 → demais**. O doc 09 reorienta a plataforma de "equipe do Victor" para **produto de marketing multi-marca** (Victor é o primeiro cliente; SaaS é o horizonte).

## 1. O que esta plataforma é

Uma **plataforma de marketing orgânico operada por agentes de IA, aplicável a qualquer marca** (doc 09). O dono da marca atua como CEO: define a missão, aprova estratégia, audita resultados — e é aconselhado pelo Diretor, que funciona como seu CMO de IA. A plataforma planeja, produz, publica, mede e **se auto-ajusta**, funcionando integralmente na ausência do CEO. O Victor é o primeiro cliente; o horizonte é abrir como SaaS.

Na V1, opera duas marcas com perfis distintos (e é construída para suportar N marcas/tenants sem reescrita):

| Marca | Natureza | Participação do CEO (Victor) |
|---|---|---|
| **éozoré** | Marca pessoal, educação em dados/IA/ML; alvo: virar referência | Roteiros a 4 mãos + gravação de vídeo (manual). Todo o resto é autônomo. |
| **AINewz** | Portal de notícias de IA resumidas por IA (projeto GCP separado); portal + newsletter + LinkedIn já operam | Zero produção manual. Tudo deriva das notícias. Victor calibra curadoria e lê relatórios. |

## 2. Princípios inegociáveis

1. **Estratégia é configuração versionada, nunca código.** Público, objetivo, funil e pilares vivem em documentos de estratégia (`strategies/`). Nenhum prompt de agente pode ter público, tom ou tema hardcoded. Mudar de público = publicar nova versão de estratégia.
2. **A trilha autônoma nunca espera o Victor.** Itens que exigem o Victor (`requer_ceo: true`) vão para a fila dele; todo o resto flui. Se ele ficar semanas ausente, o calendário se preenche com formatos autônomos (degradação graciosa).
3. **Candor é contrato.** Agentes estratégicos entregam recomendações no formato posição + evidência + contra-argumento + confiança. Existe um agente Crítico cuja função é atacar o plano. Bajulação é bug. Ver documento 03.
4. **Memória institucional é cidadã de primeira classe.** Todo conteúdo publicado entra no grafo de conteúdo (conceitos, dependências, URL, performance). Produção nova SEMPRE consulta o grafo e referencia conteúdo anterior com link acionável nativo do canal.
5. **O sistema aprende com método científico.** Hipótese → experimento (~20% dos slots) → medição → aprendizado promovido ou descartado. Aprendizados viram knowledge base mantida pelos próprios agentes, com curadoria do Diretor.
6. **Custo é restrição de primeira ordem.** Orçamento mensal com três gatilhos (R$200 aviso, R$400 modo economia, R$600 bloqueio). Ver documento 05. Nenhuma feature pode ser implementada sem registrar custo no ledger.
7. **Voz humana imperceptível.** Conteúdo final passa pelo Revisor, com guia de voz negativo (anti-padrões de IA) e few-shot de posts reais do Victor. Conteúdo que "cheira a IA" é reprovado.

## 3. As duas trilhas

### Trilha colaborativa (depende do Victor)
Aplica-se apenas a **roteiros de YouTube longo e reels/shorts gravados** da marca éozoré.

```
Estrategista decide que o tema merece vídeo
  → Roteirista produz sozinho: pesquisa + 3 opções de gancho + estrutura
    de retenção + rascunho completo + shot list + texto de teleprompter
  → Item entra na fila do CEO (painel/chat)
  → Victor ajusta a 4 mãos em poucos turnos e aprova (~20 min)
  → Tarefa "gravar" fica pendente com tudo anexado
  → Victor sobe o vídeo no bucket quando puder
  → A PARTIR DO UPLOAD, a trilha autônoma assume: transcrição, cortes,
    legendas, derivados (posts, carrossel, blog), publicação
```

### Trilha autônoma (roda sem o Victor)
Todo o resto: posts escritos, threads, carrosséis, cards visuais, vídeos renderizados (HTML/Remotion sem imagem do Victor), blog, newsletter, e 100% do AINewz.

```
Estrategista preenche slots do calendário (pauta vinda de: estratégia
vigente + grafo de lacunas + aprendizados do Analista + notícias AINewz)
  → Produção (Redator / Designer / Editor de vídeo)
  → Revisor (voz, qualidade, factualidade, referências do grafo)
  → Publicador (adapter do canal, na janela ótima)
  → Analista mede e realimenta
```

## 4. Ritmo operacional (heartbeat)

A equipe trabalha em cadência própria via Cloud Scheduler — eventos complementam, o relógio garante:

| Quando | Rodada | O que acontece |
|---|---|---|
| Domingo 18h | **Planejamento semanal** | Analista entrega leitura da semana → Estrategista propõe calendário → Crítico ataca → Diretor consolida → vai para aprovação do Victor (1 toque). Sem resposta em 24h: aplica plano com autonomia configurada. |
| Diário 6h | **Produção** | Diretor distribui os slots do dia para os agentes de produção. |
| Diário (janelas por canal) | **Publicação** | Publicador executa a fila agendada. |
| Diário 22h | **Analytics** | Analista coleta métricas de todas as APIs e atualiza o grafo. |
| Sexta 17h | **Retro + memória** | Agentes escrevem retros; Diretor cura memórias; gera relatório semanal do CEO. |
| Evento | **Notícia AINewz** | Score editorial → se top N do dia, dispara produção multi-formato. |
| Evento | **Vídeo no bucket** | Pipeline de derivados do vídeo. |

## 5. Interface do CEO (cockpit)

Frontend Next.js já existente, expandido com:

1. **Fila de aprovações** — roteiros a 4 mãos + itens `approve_required` + decisões estratégicas recomendadas pelo Analista. Ações: aprovar / editar via chat / rejeitar com motivo (motivo alimenta o decision log).
2. **Calendário visual** — o que está agendado por marca/canal, com status.
3. **Relatório semanal do Diretor** — o que foi publicado, performance por pilar/canal/funil, aprendizados novos, mudanças de "crença" dos agentes, recomendações com contra-argumentos, custo da semana vs orçamento.
4. **Controles** — nível de autonomia por marca+canal (`draft_only` / `approve_required` / `auto_publish`), `nivel_de_franqueza`, "modo férias" (N dias só com trilha autônoma + buffer pré-aprovado), pesos do score editorial do AINewz.

Notificações (Telegram ou push): SOMENTE quando há decisão humana pendente, falha real ou gatilho de custo. Nunca notificar sucesso.

## 6. Glossário rápido

- **Content atom**: unidade derivada de uma fonte (vídeo transcrito ou notícia): tese, pontos-chave, citações, timestamps. Toda derivação parte do átomo.
- **Slot**: posição no calendário (marca + canal + dia + hora + pilar + estágio de funil).
- **Buffer**: estoque de conteúdo aprovado e agendável, mínimo de 7 dias por marca, para ausências e modo economia.
- **Brand profile**: documento invariante da marca (doc 04). **Estratégia**: documento versionado de objetivo/público/pilares (doc 02, seção strategies).
