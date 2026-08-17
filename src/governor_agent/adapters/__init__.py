"""Governance source adapters."""

from governor_agent.adapters.contracts import (
    FactoryManifest,
    GoldenPathDocument,
    GovernanceSource,
    GovernanceSourceError,
    ValidatorKind,
    ValidatorSpec,
)
from governor_agent.adapters.synthetic import SyntheticFactoryAdapter

__all__ = [
    "FactoryManifest",
    "GoldenPathDocument",
    "GovernanceSource",
    "GovernanceSourceError",
    "SyntheticFactoryAdapter",
    "ValidatorKind",
    "ValidatorSpec",
]
