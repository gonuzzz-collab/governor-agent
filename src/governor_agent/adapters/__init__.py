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
from governor_agent.adapters.inventory import (
    FactorySourceInventory,
    GoNucleoFactoryInventoryAdapter,
    RealFactoryInventory,
    SourceReadiness,
)

__all__ = [
    "FactoryManifest",
    "GoldenPathDocument",
    "GovernanceSource",
    "GovernanceSourceError",
    "FactorySourceInventory",
    "GoNucleoFactoryInventoryAdapter",
    "RealFactoryInventory",
    "SourceReadiness",
    "SyntheticFactoryAdapter",
    "ValidatorKind",
    "ValidatorSpec",
]
