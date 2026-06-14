"""Contrato de candor — doc 11 §4.3, doc 03 §2.

Toda recomendação de agente estratégico DEVE retornar este tipo.
Sem os quatro campos preenchidos, o Diretor rejeita.
"""

from pydantic import BaseModel, Field


class Recommendation(BaseModel):
    """Formato obrigatório de recomendação com candor."""

    posicao: str  # recomendação direta, sem hedging
    evidencia: list[str] = Field(default_factory=list)  # refs; vazio => declarar intuição
    contra_argumento: str  # o melhor caso CONTRA a própria posição
    confianca: float = Field(ge=0, le=1)
    o_que_mudaria_confianca: str

    def is_valid(self) -> bool:
        """Valida que todos os campos obrigatórios estão preenchidos."""
        return bool(self.posicao and self.contra_argumento and self.o_que_mudaria_confianca)
