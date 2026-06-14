"""core_domain — tipos de domínio da plataforma, SEM dependência de infra."""

from core_domain.enums import (
    Autonomia,
    Canal,
    CostAccount,
    Funil,
    ItemStatus,
    PlatformStatus,
    TaskKind,
    TeamId,
)
from core_domain.exceptions import (
    BudgetExceededError,
    PlatformPausedError,
    ScopeViolationError,
    TeamInactiveError,
)
from core_domain.messages import AgentRequest, AgentResponse
from core_domain.models import (
    BacklogItem,
    BrandConfig,
    ChannelConfig,
    ContentNode,
    CostEntry,
    MediaAsset,
    Performance,
    RiscoSensibilidade,
    Scope,
    Slot,
    TeamSubscription,
    TenantConfig,
)
from core_domain.recommendation import Recommendation

__all__ = [
    "AgentRequest",
    "AgentResponse",
    "Autonomia",
    "BacklogItem",
    "BrandConfig",
    "BudgetExceededError",
    "Canal",
    "ChannelConfig",
    "ContentNode",
    "CostAccount",
    "CostEntry",
    "Funil",
    "ItemStatus",
    "MediaAsset",
    "Performance",
    "PlatformPausedError",
    "PlatformStatus",
    "Recommendation",
    "RiscoSensibilidade",
    "Scope",
    "ScopeViolationError",
    "Slot",
    "TaskKind",
    "TeamId",
    "TeamInactiveError",
    "TeamSubscription",
    "TenantConfig",
]
