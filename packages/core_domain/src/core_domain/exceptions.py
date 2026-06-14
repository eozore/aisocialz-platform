"""Exceções de domínio compartilhadas."""


class PlatformPausedError(Exception):
    """Levantada quando platform_status == paused e uma operação é tentada."""


class BudgetExceededError(Exception):
    """Levantada quando o teto de custo (por item ou diário) é excedido."""

    def __init__(self, message: str = "Orçamento excedido", custo_brl: float = 0.0):
        super().__init__(message)
        self.custo_brl = custo_brl


class ScopeViolationError(Exception):
    """Levantada quando uma operação tenta burlar o escopo de tenant."""


class TeamInactiveError(Exception):
    """Levantada quando se tenta usar um time que não está ativo."""

    def __init__(self, team_id: str):
        super().__init__(f"Time '{team_id}' não está ativo para este tenant")
        self.team_id = team_id
