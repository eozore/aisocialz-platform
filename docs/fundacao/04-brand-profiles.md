# 04 — Brand Profiles (preenchidos)

> Invariantes da marca. A estratégia (público/objetivo/pilares) vive em `strategies/` (doc 02) e muda sem tocar aqui. Campos `[PREENCHER]` exigem o Victor antes do go-live.

## brands/eozore

```json
{
  "brand_id": "eozore",
  "nome": "éozoré",
  "missao": "provar que dados e IA são aprendíveis por qualquer pessoa disciplinada, unindo técnica, estatística e visão de negócio",
  "idioma": "pt-BR",
  "modo": "sandbox",
  "estetica": {
    "paleta": {"primaria": "terracota [PREENCHER hex]", "secundaria": "bege [PREENCHER hex]", "apoio": "[PREENCHER]"},
    "tipografia": "[PREENCHER]",
    "templates_html": ["carrossel_educativo", "card_citacao", "capa_post", "thumbnail_youtube", "card_dado_estatistico"],
    "regra": "estética vive nos templates versionados; agentes não inventam visual"
  },
  "voz": {
    "descricao": "professor próximo que já esteve do outro lado: conversacional, direto, usa analogias de negócio e futebol, rigor estatístico sem arrogância, humor leve",
    "few_shot": "[PREENCHER: 10-15 posts/roteiros reais por canal — OBRIGATÓRIO antes de produção real]",
    "anti_padroes": [
      "aberturas clichê ('no mundo acelerado de hoje', 'você já parou para pensar')",
      "'vamos mergulhar', 'desvendar', 'game changer'",
      "listas numeradas previsíveis como estrutura padrão",
      "excesso de travessões e de emojis em sequência",
      "tom de palestra motivacional; promessas infladas ('domine X em 7 dias')",
      "hedging vazio ('pode ser que talvez')"
    ],
    "assinatura": ["citar dados com fonte", "admitir o que é difícil", "terminar com próximo passo concreto"]
  },
  "canais": {
    "youtube":   {"ativo": true, "autonomia": "approve_required", "janelas": ["ter 19:00", "sab 10:00"], "formatos": ["youtube_longo", "corte_short"]},
    "instagram": {"ativo": true, "autonomia": "approve_required", "janelas": ["seg-sex 12:00", "seg-sex 19:30"], "formatos": ["carrossel", "reel_gravado", "reel_renderizado", "card"]},
    "linkedin":  {"ativo": true, "autonomia": "approve_required", "janelas": ["ter 08:30", "qui 08:30"], "formatos": ["post_linkedin", "carrossel_pdf"]},
    "threads":   {"ativo": true, "autonomia": "auto_publish", "janelas": ["diario 13:00"], "formatos": ["thread"]},
    "blog":      {"ativo": true, "autonomia": "auto_publish", "janelas": ["qua 07:00"], "formatos": ["blog"]},
    "tiktok":    {"ativo": false}
  },
  "nivel_de_franqueza": 0.9,
  "trilha_colaborativa": {"formatos_requer_ceo": ["youtube_longo", "reel_gravado"], "fila_max": 3, "fallback_ausencia": "preencher slots com formatos autônomos do mesmo pilar"},
  "buffer_minimo_dias": 7,
  "estrategia_ativa": "strategies/eozore/versions/v1-2026Q2"
}
```

(As janelas acima são chute inicial conservador — viram hipóteses que o Analista testa e substitui por learnings.)

## brands/ainewz

```json
{
  "brand_id": "ainewz",
  "nome": "AINewz",
  "missao": "ser a curadoria confiável de notícias de IA em português: rápida, factual e com leitura crítica do que importa",
  "idioma": "pt-BR",
  "modo": "sandbox",
  "estetica": {
    "paleta": "[PREENCHER — identidade atual do portal]",
    "templates_html": ["card_noticia", "carrossel_resumo_dia", "card_dado", "capa_newsletter"]
  },
  "voz": {
    "descricao": "editor de tecnologia experiente: informativo, ágil, opinião sempre rotulada como análise e separada do fato, zero sensacionalismo",
    "few_shot": "[PREENCHER: 10-15 publicações reais do portal/LinkedIn]",
    "anti_padroes": ["clickbait", "URGENTE/BOMBA", "afirmação sem fonte", "tradução literal de manchete em inglês"],
    "regra_dura": "toda afirmação factual rastreável à notícia-fonte; fonte citada no formato do canal"
  },
  "fonte_principal": {
    "tipo": "pubsub_cross_project",
    "topic": "projects/[AINEWZ_PROJECT_ID]/topics/noticia-publicada",
    "conteudo_completo": "[PREENCHER: Firestore read-only ou endpoint existente]"
  },
  "score_editorial": {
    "descricao": "cada notícia recebe score 0-1; top N do dia disparam produção multi-formato",
    "pesos": {"relevancia_publico": 0.35, "ineditismo": 0.25, "potencial_discussao": 0.20, "fit_pilares": 0.20},
    "top_n_dia": 3,
    "minimo_para_producao": 0.6,
    "ajustavel_no_cockpit": true
  },
  "canais": {
    "linkedin":   {"ativo": true, "autonomia": "auto_publish", "nota": "JÁ FUNCIONA no projeto AINewz — não duplicar; este projeto só publica formatos NOVOS (ex.: carrossel) após desligar o caminho antigo OU manter o caminho antigo e só adicionar formatos que ele não cobre",
                   "janelas": ["seg-sex 09:00"]},
    "newsletter": {"ativo": true, "autonomia": "auto_publish", "nota": "mecanismo existente; integrar, não recriar"},
    "instagram":  {"ativo": true, "autonomia": "auto_publish", "janelas": ["diario 12:30", "diario 18:30"], "formatos": ["card_noticia", "carrossel_resumo_dia"]},
    "threads":    {"ativo": true, "autonomia": "auto_publish", "janelas": ["diario 09:30", "diario 14:00"]},
    "tiktok":     {"ativo": false}
  },
  "nivel_de_franqueza": 0.9,
  "trilha_colaborativa": null,
  "buffer_minimo_dias": 2,
  "estrategia_ativa": "strategies/ainewz/versions/v1-2026Q2"
}
```

## strategies/ainewz/versions/v1-2026Q2 (resumo)

Objetivo: crescer audiência recorrente do portal/newsletter usando redes como topo de funil. Persona primária: profissionais de tecnologia e negócio que querem acompanhar IA sem ler 50 fontes em inglês. Pilares: lançamentos e modelos (0.35), IA + negócios no Brasil (0.30), regulação e governança (0.20), pesquisa explicada (0.15). Funil: topo = cards/threads/carrosséis nas redes; meio = portal; fundo = newsletter. **Objetivo de conversão (fase inicial): `tipo: audiencia`, métrica primária = novos assinantes da newsletter.** É o alvo que o Estrategista otimiza e o Analista mede — não vendas. Metas numéricas: `[PREENCHER]`.

## Sinergia entre marcas (regra explícita)

Notícia AINewz com score alto E fit com pilar do éozoré → o Estrategista pode gerar pauta para o **éozoré** com ângulo educacional próprio ("a notícia X provou por que você precisa entender Y"), com crédito/link para o AINewz. Fluxo unidirecional (AINewz → éozoré); o éozoré não alimenta o portal de notícias.
