"""Routing de modelos por natureza da tarefa + modo de custo — doc 03 §1, doc 11 §6.

Parametrizável via platform/model_routing (Firestore).
Em modo economia, rebaixa um nível (doc 05 §1).
"""

from core_domain.enums import PlatformStatus, TaskKind

# Routing padrão (doc 03 §1)
ROUTING_NORMAL: dict[TaskKind, str] = {
    TaskKind.ESTRUTURAL: "gemini-2.5-flash",
    TaskKind.ANALITICA: "gemini-2.5-pro",
    TaskKind.CRIATIVA: "claude-opus-4-6",
    TaskKind.CONSELHO: "claude-opus-4-6",
    TaskKind.EMBEDDING: "text-embedding-005",
}

# Routing em modo economia — rebaixa um nível (doc 05 §1)
ROUTING_ECONOMIA: dict[TaskKind, str] = {
    TaskKind.ESTRUTURAL: "gemini-2.5-flash",  # já é o mais barato
    TaskKind.ANALITICA: "gemini-2.5-flash",
    TaskKind.CRIATIVA: "claude-sonnet-4-6",  # Opus -> Sonnet
    TaskKind.CONSELHO: "claude-sonnet-4-6",
    TaskKind.EMBEDDING: "text-embedding-005",
}


def resolve_model(task_kind: TaskKind, platform_status: PlatformStatus) -> str:
    """Resolve qual modelo usar dada a natureza da tarefa e o status da plataforma."""
    if platform_status == PlatformStatus.ECONOMIA:
        return ROUTING_ECONOMIA[task_kind]
    return ROUTING_NORMAL[task_kind]
