"""Factory do cliente Firestore — suporta emulador local e produção.

Uso:
    from persistence.firestore_client import get_firestore_client
    db = get_firestore_client()  # auto-detecta emulador via FIRESTORE_EMULATOR_HOST
"""

import os

from google.cloud.firestore_v1 import AsyncClient


def get_firestore_client(project_id: str | None = None) -> AsyncClient:
    """Retorna um AsyncClient do Firestore.

    Se FIRESTORE_EMULATOR_HOST estiver setado, conecta ao emulador local.
    Caso contrário, conecta ao Firestore real (exige credenciais GCP).
    """
    emulator_host = os.environ.get("FIRESTORE_EMULATOR_HOST")

    if emulator_host:
        # Emulador local — não precisa de credenciais reais
        return AsyncClient(project=project_id or "demo-aisocialz")
    else:
        # Produção — usa Application Default Credentials
        return AsyncClient(project=project_id)


def is_emulator() -> bool:
    """Retorna True se estamos rodando contra o emulador."""
    return bool(os.environ.get("FIRESTORE_EMULATOR_HOST"))
