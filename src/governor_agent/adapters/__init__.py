"""Governance source adapters."""

from governor_agent.adapters.contracts import (
    FactoryEvidenceSource,
    FactoryManifest,
    GoldenPathDocument,
    GovernanceSource,
    GovernanceSourceError,
    ValidatorUnavailableError,
    ValidatorKind,
    ValidatorSpec,
)
from governor_agent.adapters.synthetic import SyntheticFactoryAdapter
from governor_agent.adapters.inventory import (
    FactorySourceFormat,
    FactorySourceInventory,
    GoNucleoFactoryInventoryAdapter,
    RealFactoryAdapter,
    RealFactoryInventory,
    SourceReadiness,
)

__all__ = [
    "FactoryManifest",
    "FactoryEvidenceSource",
    "FactorySourceFormat",
    "GoldenPathDocument",
    "GovernanceSource",
    "GovernanceSourceError",
    "FactorySourceInventory",
    "GoNucleoFactoryInventoryAdapter",
    "RealFactoryInventory",
    "RealFactoryAdapter",
    "SourceReadiness",
    "SyntheticFactoryAdapter",
    "ValidatorUnavailableError",
    "ValidatorKind",
    "ValidatorSpec",
]
