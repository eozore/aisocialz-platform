"""svc-agents — todos os agentes ADK co-localizados (doc 11 §1, ADR-002)."""

from agents.analista import AnalistaAgent
from agents.base import PlatformAgent
from agents.comunidade import ComunidadeAgent
from agents.curador import CuradorAgent
from agents.diretor import DiretorAgent
from agents.estrategista import EstrategistaAgent
from agents.radar import RadarAgent
from agents.redator import RedatorAgent
from agents.revisor import RevisorAgent

__all__ = [
    "AnalistaAgent",
    "ComunidadeAgent",
    "CuradorAgent",
    "DiretorAgent",
    "EstrategistaAgent",
    "PlatformAgent",
    "RadarAgent",
    "RedatorAgent",
    "RevisorAgent",
]
