# 07 — Render Visual e Template Studio

## 1. Decisão: HTML como motor visual da fábrica

**Imagens**: templates HTML+CSS versionados → Puppeteer (serviço de render no Cloud Run) → PNG/JPG nas dimensões do canal. É o caminho padrão para TODO conteúdo de marca (carrossel, card, capa, thumbnail). Justificativa: controle estético total via CSS, agentes fluentes em HTML, custo ~zero, determinístico, versionável.

- **Imagen (geração por IA)**: apenas complemento para conteúdo fotográfico/ilustrativo pontual, nunca para peças do brand system. Toda chamada passa pelo wrapper de custo.
- **Satori** (HTML→PNG sem browser): otimização futura para cards simples se o volume justificar; não é fundação.
- **Canva**: ferramenta de design manual do Victor; NÃO é motor da fábrica (dependência externa, fora do git).

**Vídeo — três camadas, da mais barata para a mais cara:**

| Camada | Ferramenta | Uso | Custo |
|---|---|---|---|
| 1 | **FFmpeg** | Cortes do vídeo gravado, legendas queimadas, concat, overlay de cards estáticos (renderizados via HTML) | Irrisório — caminho padrão para derivados de gravação |
| 2 | **Remotion** | Vídeos 100% renderizados (card animado de notícia, dado animado) | CPU caro — formato só é habilitado com evidência do Analista; suspenso em modo economia (doc 05) |
| 3 | Editor GUI | — | **Não existe e não será construído.** O "editor" é o agente Editor de vídeo + FFmpeg; o humano só faz preview e aprovação no cockpit |

## 2. Anatomia de um template

Cada template vive em `templates/{brand}/{template_id}/` no monorepo (espelhado no bucket `templates-html` no deploy):

```
templates/eozore/carrossel_educativo/
  template.html        # HTML+CSS autocontido, placeholders {{var}}
  manifest.json
  sample_data.json     # dados de exemplo para preview
```

```json
// manifest.json
{
  "template_id": "carrossel_educativo",
  "brand": "eozore",
  "formato": "carrossel",
  "dimensoes": {"largura": 1080, "altura": 1350},
  "paginas": "1-10",
  "variaveis": [
    {"nome": "titulo", "tipo": "texto", "max_chars": 60},
    {"nome": "corpo", "tipo": "texto_rico", "max_chars": 280},
    {"nome": "numero_pagina", "tipo": "auto"},
    {"nome": "cta_final", "tipo": "texto", "max_chars": 40}
  ],
  "status": "sandbox | aprovado | aposentado",
  "versao": "1.2.0"
}
```

Regras: o Designer só usa templates com `status: aprovado`; preencher variável acima de `max_chars` é erro de validação (devolve ao Redator, nunca trunca silenciosamente); após preencher, o Designer roda um screenshot de checagem e um validador simples (overflow de texto, contraste mínimo) antes de enviar à revisão.

## 3. Template Studio (módulo do cockpit)

O espaço onde o Victor vê e edita os layouts. Princípio central: **o preview usa o MESMO serviço Puppeteer da produção** — o que se vê no Studio é pixel-perfect o que sai publicado.

Funcionalidades:

1. **Galeria por marca** — todos os templates com thumbnail (render do `sample_data.json`), status e versão.
2. **Preview real** — render nas dimensões reais do canal, com troca rápida entre dados de exemplo e dados de uma peça real do backlog ("como ficaria o post de amanhã neste template?").
3. **Edição por código** — editor Monaco embutido sobre o `template.html`; salvar = commit no monorepo + invalidação do cache do bucket + re-render do preview.
4. **Edição por chat** — instrução em linguagem natural roteada à IA construtora ("aumenta o respiro do título", "cria variante escura deste card"), que propõe o diff, mostra preview lado a lado (antes/depois) e commita após aprovação.
5. **Ciclo de vida** — template novo nasce `sandbox`; botão "aprovar" o libera para os agentes; "aposentar" o remove do rol sem apagar histórico (peças antigas continuam reproduzíveis pela versão).
6. **Render de teste** — botão que enfileira um render avulso e mostra custo estimado no ledger (`agente: "studio"`).

## 4. Para a IA construtora

- Implementar o serviço de render como API única (`render(template_id, versao, dados, formato_saida)`) usada por Designer, Editor de vídeo (overlays), Studio e sandbox — um só caminho de render no sistema inteiro.
- Fase 1 (doc 09 §7) passa a incluir o Template Studio em versão mínima (galeria + preview + edição por código). Edição por chat e comparação antes/depois podem vir na Fase 2.
- Migrar o padrão atual do Victor (build script Python de HTML autocontido) para este formato de template com manifest — aproveitar os HTMLs já criados como primeiros templates do éozoré.
