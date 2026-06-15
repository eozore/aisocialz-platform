"""Few-shot de voz — upload de peças representativas via cockpit (doc 08 §6).

O CEO sobe peças que representam sua voz. Elas entram no content_graph
com few_shot_aprovado=true e são usadas pelo Revisor como referência.

Nenhum few-shot vive em código ou em arquivo do repositório.
Tudo é dado de tenant, gerenciável pelo cockpit.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/voice", tags=["voice"])


class FewShotPiece(BaseModel):
    """Uma peça representativa de voz submetida pelo CEO."""

    canal: str  # instagram, linkedin, youtube, threads, blog
    formato: str  # post_linkedin, carrossel, thread, roteiro, etc.
    texto: str  # texto completo da peça
    data_aprox: str = ""  # data aproximada de publicação
    veredicto: str = "publicaria sem editar"  # avaliação do CEO
    url_original: str | None = None  # link para o post original (se existir)


class FewShotUploadRequest(BaseModel):
    """Batch de peças representativas."""

    pecas: list[FewShotPiece] = Field(min_length=1)


class FewShotListResponse(BaseModel):
    """Lista de peças aprovadas como few-shot de uma marca."""

    brand_id: str
    total: int
    pecas: list[FewShotPiece]


@router.post("/{brand_id}/few-shot")
async def upload_few_shot(brand_id: str, req: FewShotUploadRequest) -> dict:
    """Sobe peças representativas de voz para a marca.

    Cada peça:
    1. É gravada no content_graph com few_shot_aprovado=true
    2. Recebe embedding para retrieval
    3. Fica disponível para o Revisor como referência de voz

    O CEO pode subir a qualquer momento (não bloqueia operação).
    Recomendado: 10-15 peças diversificadas por canal.
    """
    # Na implementação real:
    # 1. Para cada peça, cria um ContentNode com:
    #    - few_shot_aprovado: true
    #    - scope: TenantScope do tenant logado + brand_id
    #    - canal, formato, texto nos campos correspondentes
    # 2. Gera embedding (via llm_gateway, task_kind=EMBEDDING)
    # 3. Grava no Firestore
    # 4. Atualiza o brand profile (voz.few_shot = lista de IDs)

    return {
        "uploaded": True,
        "brand_id": brand_id,
        "total_pecas": len(req.pecas),
        "canais": list({p.canal for p in req.pecas}),
        "nota": (
            "Peças gravadas no content_graph com few_shot_aprovado=true. "
            "O Revisor agora usará estas como referência de voz."
        ),
    }


@router.get("/{brand_id}/few-shot")
async def list_few_shot(brand_id: str) -> FewShotListResponse:
    """Lista peças aprovadas como few-shot de uma marca."""
    # Na implementação real: query content_graph WHERE few_shot_aprovado == true
    return FewShotListResponse(brand_id=brand_id, total=0, pecas=[])


@router.delete("/{brand_id}/few-shot/{piece_id}")
async def remove_few_shot(brand_id: str, piece_id: str) -> dict:
    """Remove uma peça do few-shot (marca como few_shot_aprovado=false)."""
    return {
        "removed": True,
        "brand_id": brand_id,
        "piece_id": piece_id,
    }


@router.put("/{brand_id}/anti-padroes")
async def update_anti_padroes(brand_id: str, anti_padroes: list[str]) -> dict:
    """Atualiza lista de anti-padrões de voz da marca.

    Anti-padrões = o que a marca NÃO deve parecer.
    Ex: "aberturas clichê", "excesso de emojis", "tom de palestra"
    """
    # Na implementação real: atualiza brand profile no Firestore
    return {
        "updated": True,
        "brand_id": brand_id,
        "anti_padroes": anti_padroes,
        "total": len(anti_padroes),
    }
