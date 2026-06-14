"""Guardas do anti-atalho — doc 11 §11.

Estes testes FALHAM se:
1. Algum acesso a Firestore burlar o package `persistence` (escopo de tenant)
2. Alguma chamada a Vertex/Anthropic burlar o package `llm_gateway`
3. core_domain importar módulos de infra

Existem ANTES de existir feature. CI deve rodar isto a cada PR.
"""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Módulos que indicam acesso direto ao Firestore
FIRESTORE_MODULES = {
    "google.cloud.firestore",
    "google.cloud.firestore_v1",
    "google.cloud.firestore_admin_v1",
}

# Módulos que indicam chamada direta a LLM
LLM_MODULES = {
    "vertexai",
    "anthropic",
    "google.generativeai",
    "google.cloud.aiplatform",
}

# Módulos de infra proibidos em core_domain
INFRA_MODULES = (
    FIRESTORE_MODULES
    | LLM_MODULES
    | {
        "google.cloud",
        "httpx",
        "fastapi",
        "uvicorn",
    }
)


def _collect_imports(file_path: Path) -> set[str]:
    """Extrai todos os módulos importados de um arquivo Python."""
    try:
        tree = ast.parse(file_path.read_text(), filename=str(file_path))
    except SyntaxError:
        return set()

    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def _check_forbidden(source_dir: Path, forbidden: set[str], context: str) -> list[str]:
    """Verifica que nenhum arquivo em source_dir importa módulos proibidos."""
    violations: list[str] = []
    if not source_dir.exists():
        return violations

    for py_file in source_dir.rglob("*.py"):
        imports = _collect_imports(py_file)
        for imp in imports:
            for forbidden_mod in forbidden:
                if imp == forbidden_mod or imp.startswith(f"{forbidden_mod}."):
                    rel = py_file.relative_to(ROOT)
                    violations.append(f"  {rel}: importa '{imp}' ({context})")
    return violations


def test_core_domain_no_infra() -> None:
    """core_domain NÃO pode importar módulos de infra (doc 11 §2)."""
    violations = _check_forbidden(
        ROOT / "packages" / "core_domain" / "src",
        INFRA_MODULES,
        "core_domain não importa infra",
    )
    assert not violations, "core_domain importou módulos de infra proibidos:\n" + "\n".join(
        violations
    )


def test_firestore_only_via_persistence() -> None:
    """Nenhum package/service (exceto persistence) acessa Firestore diretamente."""
    all_violations: list[str] = []

    # Packages que NÃO podem tocar Firestore
    for pkg in ["adapters", "llm_gateway", "render_client", "observability"]:
        src = ROOT / "packages" / pkg / "src"
        all_violations.extend(
            _check_forbidden(src, FIRESTORE_MODULES, f"{pkg}: Firestore só via persistence")
        )

    # Services que NÃO podem tocar Firestore direto
    for svc in ["agents", "render", "publisher", "cockpit_api", "cost_guardian"]:
        src = ROOT / "services" / svc / "src"
        all_violations.extend(
            _check_forbidden(src, FIRESTORE_MODULES, f"svc-{svc}: Firestore só via persistence")
        )

    assert not all_violations, "Acesso direto a Firestore fora de persistence:\n" + "\n".join(
        all_violations
    )


def test_llm_only_via_gateway() -> None:
    """Nenhum package/service (exceto llm_gateway) chama Vertex/Anthropic direto."""
    all_violations: list[str] = []

    # Packages que NÃO podem tocar LLM
    for pkg in ["adapters", "persistence", "render_client", "observability"]:
        src = ROOT / "packages" / pkg / "src"
        all_violations.extend(_check_forbidden(src, LLM_MODULES, f"{pkg}: LLM só via llm_gateway"))

    # Services que NÃO podem tocar LLM direto (exceto agents que usa via llm_gateway)
    for svc in ["render", "publisher", "cockpit_api", "cost_guardian"]:
        src = ROOT / "services" / svc / "src"
        all_violations.extend(
            _check_forbidden(src, LLM_MODULES, f"svc-{svc}: LLM só via llm_gateway")
        )

    assert not all_violations, "Chamada direta a LLM fora de llm_gateway:\n" + "\n".join(
        all_violations
    )
