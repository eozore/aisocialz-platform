"""svc-render — API de render único (doc 07 §4).

Caminho único de render no sistema: Designer, Editor de vídeo, Studio e sandbox
todos usam esta API.

render(template_id, versao, dados, formato_saida) -> outputs gs://

Implementação:
- Puppeteer: HTML → PNG/JPG (caminho padrão para imagens)
- FFmpeg: cortes, legendas, overlays (Fase 2)
- Remotion: vídeos renderizados (só com evidência do Analista, suspenso em economia)
"""

from fastapi import FastAPI, HTTPException

from render_client.types import RenderRequest, RenderResult

app = FastAPI(
    title="AISocialZ Render Service",
    description="Serviço de render — Puppeteer/FFmpeg/Remotion",
    version="0.1.0",
)


@app.post("/render", response_model=RenderResult)
async def render(request: RenderRequest) -> RenderResult:
    """Endpoint principal de render.

    Recebe template + dados + assets, retorna URLs dos arquivos gerados.
    Na V1, executa Puppeteer para HTML→imagem.
    """
    # Validações básicas
    if not request.template_id:
        raise HTTPException(status_code=400, detail="template_id obrigatório")
    if not request.template_versao:
        raise HTTPException(status_code=400, detail="template_versao obrigatório")

    # Na implementação completa:
    # 1. Busca template do bucket/git (templates/{brand}/{template_id}/template.html)
    # 2. Preenche variáveis ({{var}})
    # 3. Injeta assets (imagens do acervo)
    # 4. Renderiza via Puppeteer nas dimensões especificadas
    # 5. Upload do resultado para gs://assets-renderizados/
    # 6. Valida overflow de texto, contraste
    # 7. Retorna URL(s) gerada(s)

    # Stub para permitir integração antes do Puppeteer real
    output_path = (
        f"gs://assets-renderizados/{request.scope.tenant_id}/"
        f"{request.scope.brand_id}/{request.template_id}/"
        f"render-stub.{request.saida}"
    )

    return RenderResult(
        ok=True,
        outputs=[output_path],
        overflow_detectado=False,
        custo_brl=0.001,  # Custo irrisório de CPU
    )


@app.get("/health")
async def health() -> dict:
    """Health check."""
    return {"status": "ok", "service": "svc-render"}
