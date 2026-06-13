# 10 — Formatos, Templates e Acervo de Mídia

> Resolve a pergunta "como o CEO controla o design dentro de um formato sem saber design?" e "como a marca usa seu banco de imagens?". Princípio geral V1: **o mais simples que funciona**; sofisticação é evolução.

## 1. As quatro camadas de um conteúdo visual

Tornar explícito o que estava embolado em "carrossel":

| Camada | O que é | Quem decide |
|---|---|---|
| **Formato** | mecânica do canal (carrossel = 2-10 imgs deslizáveis, 1080x1350) | fixo pela plataforma (catálogo) |
| **Estrutura** | anatomia narrativa (capa + N slides + CTA) | template define; Estrategista/Redator preenchem |
| **Template (tema visual)** | aparência: cores, tipografia, onde entra texto/imagem | CEO aprova o conjunto; Designer escolhe dentro dele |
| **Conteúdo** | o texto/dado/imagem de hoje | agentes preenchem |

O CEO **não desenha pixel**. Ele aprova o *conjunto de templates* disponíveis e, no máximo, expressa regras em linguagem de negócio. A estética mora nos templates aprovados.

## 2. Catálogo de formatos (global + brandável)

`platform/format_catalog/{format_id}`:

```json
{
  "format_id": "carrossel",
  "canal": ["instagram", "linkedin"],
  "mecanica": {"min_paginas": 2, "max_paginas": 10, "dimensoes": {"l": 1080, "a": 1350}},
  "estrutura_padrao": ["capa", "conteudo*", "cta"],
  "templates_base": ["base_tipografico", "base_com_imagem", "base_dado"]
}
```

`templates_base` são **HTML+CSS genéricos, brandáveis por qualquer marca** (recebem a paleta/tipografia do brand profile em runtime). É o que vem quando um time é "contratado" (doc 09 §3): a marca iniciante usa os base e já fica boa; a marca sofisticada cria os seus.

Por marca, o que vale é o conjunto aprovado (doc 07, status `aprovado`): `brands/{brand}/templates/` pode ter templates próprios + referências a `templates_base`. O Designer só usa `aprovado`.

**V1:** começar com 1 HTML-base por formato (o Victor fornece o primeiro; enquanto não chega, a construtora gera um base mínimo na paleta de cada marca). Variações vêm depois.

## 3. Como o Designer escolhe (regra V1, deliberadamente simples)

```
1. O item tem formato definido (ex.: carrossel) e conteúdo pronto (texto).
2. Este formato pede imagem? (template_base declara se tem slot de imagem)
   - Sim → buscar no acervo (§4) por similaridade com o tema do conteúdo.
       - achou asset com score >= LIMIAR → usa template "com_imagem" + o asset
       - não achou → usa template "tipográfico" (sem imagem)
   - Não → usa o template do formato direto.
3. Preenche, renderiza (Puppeteer), valida overflow/contraste, envia ao Revisor.
```

Sem decisão sofisticada na V1. Regras por pilar ("carreira é mais clean") e níveis de controle finos do CEO ficam para depois (doc 09 §5). Os dois níveis vivos na V1: **time decide** (default) + **CEO aprova no cockpit** (preview antes de publicar).

Regra específica AINewz (exemplo de regra simples em config, não em código): `"imagem_da_noticia_como_destaque": true` → quando a notícia traz imagem própria no acervo, o card usa o template com imagem.

## 4. Acervo de mídia (media_assets)

`brands/{brand}/media_assets/{asset_id}`:

```json
{
  "tipo": "imagem | video | logo",
  "fonte": "humano_upload | agente_pesquisa | ainewz_noticia | video_ia_futuro",
  "url": "gs://...",
  "tags": ["copa do mundo", "dados", "neymar"],
  "descricao": "texto para vetorização (gerado por Gemini Vision se faltar)",
  "embedding": [/* vetor — Firestore vector field */],
  "criado_em": "...", "ref_origem": "noticia_id | null"
}
```

Decisões do Victor incorporadas:
- **Preenchido por humano E por agente** (incl. pesquisa de imagem/vídeo), com **padrão único de entrada** (este schema). Toda entrada gera descrição + embedding para busca vetorial.
- **Vetorizado e consultável** pelos agentes (busca por similaridade tema↔asset). V1: vetor no próprio Firestore (`find_nearest`), igual ao grafo — sem Vector Search dedicado.
- **Direitos: NÃO é responsabilidade do time na V1.** Presume-se que todo asset no acervo está autorizado; o risco é do CEO (dono da marca). Sem tag de licença, sem verificação. *Feature futura:* agente verificador de direitos (registrar como evolução, não bloquear V1).
- **Fonte `video_ia_futuro`** já previsto como tipo de origem, para o repositório de vídeos editados (doc 09 §6) plugar sem redesenho.

Telas no cockpit (V1 mínima): um "acervo" por marca onde o Victor **sobe assets** (upload manual) e vê o que os agentes adicionaram. Busca e tags visíveis. Curadoria fina depois.

## 5. Time de revisão de templates (schedule) — decisão do Victor

Um time que **evolui os templates sozinho, como proposta**:
- Roda em schedule (ex.: mensal).
- Analisa performance por template (o `content_graph` registra qual template gerou cada peça; o Analista atribui performance) + pesquisa de referências visuais.
- Propõe ajustes (variação de template, novo template, aposentar um que performa mal) → entra como **proposta na fila do CEO** no Template Studio, com preview antes/depois.
- Nunca altera template aprovado sozinho; CEO aprova. Fecha o ciclo de aprendizado também na camada visual.
- *Fase: começa simples na Fase 1 (registro de template→performance); a proposta automática pode vir no fim da Fase 1 ou Fase 2.*

## 6. Para a construtora

- Estender o serviço de render (doc 07) para aceitar `asset_url` como insumo do template (imagem de fundo/destaque), além de texto.
- `content_graph` passa a registrar `template_id` + `template_versao` + `assets_usados` em cada peça (para o time de revisão de templates e o Analista).
- Busca vetorial do acervo reusa a infra do grafo (mesmo padrão Firestore). Não criar índice novo na V1.
- Catálogo de formatos é global (`platform/`); aprovação de template é por marca.
