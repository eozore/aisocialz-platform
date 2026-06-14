"""adapters — contrato + implementações de canal."""

from adapters.base import (
    ChannelAdapter,
    MetricsSnapshot,
    PublishPayload,
    PublishResult,
    ValidationIssue,
)
from adapters.credentials import CredentialResolver
from adapters.registry import AdapterRegistry

__all__ = [
    "AdapterRegistry",
    "ChannelAdapter",
    "CredentialResolver",
    "MetricsSnapshot",
    "PublishPayload",
    "PublishResult",
    "ValidationIssue",
]
