"""Tipos de mídia reestruturados — kit de marca + dimensões predefinidas.

O acervo é organizado por:
- Categoria (logo, icone, background, foto, ilustracao, pattern, video)
- Dimensão/uso (stories, feed, thumbnail, post_quadrado, header, original)
- Kit de marca: logo, cores exatas, tipografia, elementos gráficos
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class MediaCategory(StrEnum):
    """Categorias de mídia no acervo."""

    LOGO = "logo"
    ICONE = "icone"
    BACKGROUND = "background"
    FOTO = "foto"
    ILUSTRACAO = "ilustracao"
    PATTERN = "pattern"
    VIDEO = "video"
    ELEMENTO_GRAFICO = "elemento_grafico"


class MediaDimension(StrEnum):
    """Dimensões predefinidas por uso — facilita busca pelos agentes."""

    STORIES = "1080x1920"  # Stories/Reels
    FEED = "1080x1350"  # Feed IG/LinkedIn
    QUADRADO = "1080x1080"  # Post quadrado
    THUMBNAIL = "1280x720"  # YouTube thumbnail
    HEADER = "1500x500"  # LinkedIn/Twitter header
    BANNER = "1200x628"  # Link preview / OG image
    ORIGINAL = "original"  # Tamanho original (não redimensionado)


class BrandColor(BaseModel):
    """Cor exata do kit de marca."""

    nome: str  # "primaria", "secundaria", "apoio", "texto", "fundo"
    hex: str  # ex: "#C05A3C"
    uso: str = ""  # ex: "títulos e CTAs", "fundos claros"


class BrandFont(BaseModel):
    """Tipografia do kit de marca."""

    nome: str  # ex: "Inter", "Playfair Display"
    peso: str = "400"  # "400", "700", etc.
    uso: str = ""  # "títulos", "corpo", "destaques"
    url: str | None = None  # Google Fonts URL ou gs://


class BrandKit(BaseModel):
    """Kit de mídia completo da marca — configurável via cockpit.

    Não vive em código; vive no Firestore sob tenant/{tid}/brands/{bid}/brand_kit.
    """

    cores: list[BrandColor] = Field(default_factory=list)
    fontes: list[BrandFont] = Field(default_factory=list)
    logos: list[str] = Field(default_factory=list)  # IDs dos assets de logo no acervo
    elementos_graficos: list[str] = Field(default_factory=list)  # IDs de patterns/ícones


class MediaAssetV2(BaseModel):
    """Asset de mídia com categoria + dimensão (evolução do MediaAsset original).

    Facilita busca pelos agentes:
    - Designer busca por categoria + dimensão (não por vetorial solta)
    - Ex: "preciso de background em 1080x1350" → filtra direto
    """

    id: str
    tenant_id: str
    brand_id: str
    categoria: MediaCategory
    dimensao: MediaDimension = MediaDimension.ORIGINAL
    largura: int | None = None
    altura: int | None = None
    formato_arquivo: str = ""  # png, jpg, svg, mp4
    url: str  # gs://...
    tags: list[str] = Field(default_factory=list)
    descricao: str = ""
    embedding: list[float] | None = None
    fonte: str = "humano_upload"  # humano_upload | agente | noticia_externa
    ref_origem: str | None = None
