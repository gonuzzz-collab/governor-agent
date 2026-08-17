"""Privacy-preserving, read-only inventory adapter for the real GoNucleo factory.

This adapter deliberately does not implement GovernanceSource. The current factory exposes a
machine-readable project catalog, but not complete policy, capability, authority, and permit
registries with the Governor contracts. Reporting that gap is safer than inventing an integration.
"""

from __future__ import annotations

import tomllib
from collections import Counter
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from governor_agent.adapters.contracts import GovernanceSourceError
from governor_agent.domain.paths import UnsafePathError, validate_relative_path

MAX_FACTORY_FILE_BYTES = 1_000_000


class SourceReadiness(str, Enum):
    AVAILABLE = "available"
    PARTIAL = "partial"
    MISSING = "missing"


class FactorySourceInventory(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    source: str
    readiness: SourceReadiness
    normative: bool
    relative_location: str | None
    reason: str


class RealFactoryInventory(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    factory_id: str
    factory_schema: str
    catalog_schema_version: int
    project_count: int = Field(ge=0)
    adoption_counts: dict[str, int]
    portfolio_counts: dict[str, int]
    sources: tuple[FactorySourceInventory, ...]
    ready_for_governance_evaluation: bool
    privacy_boundary: str


class GoNucleoFactoryInventoryAdapter:
    """Inspect only fixed factory metadata paths; never recurse through application data."""

    FACTORY_MANIFEST = ".gonucleo-factory.toml"
    PROJECT_CATALOG = ".skills/factory-catalog.toml"
    EXISTING_TOOL_SOURCES = (
        (
            "golden_path_tool",
            ".skills/project-golden-path",
            SourceReadiness.PARTIAL,
            True,
            "Tooling is normative for project scaffolding, not a complete change-policy source.",
        ),
        (
            "factory_status_tool",
            ".skills/factory-status",
            SourceReadiness.PARTIAL,
            True,
            "Status is derived from the project catalog and project manifests.",
        ),
        (
            "change_permit_tool",
            ".skills/change-permit",
            SourceReadiness.PARTIAL,
            True,
            "A report-only permit workflow exists, but no persistent Governor permit registry exists.",
        ),
        (
            "safety_gate_tool",
            ".skills/safety-gate",
            SourceReadiness.PARTIAL,
            True,
            "Command risk classification exists, but it is not a general authority registry.",
        ),
    )
    UNIMPLEMENTED_CONTRACTS = (
        (
            "capability_registry",
            "The audited factory describes capability governance as a proposal, not an implemented registry.",
        ),
        (
            "governance_policies",
            "No complete machine-readable normative policy contract is currently defined.",
        ),
        (
            "authority_registry",
            "No machine-readable actor authority registry is currently defined.",
        ),
        (
            "permit_registry",
            "Change Permit exists as report-only workflow output, not a persistent registry contract.",
        ),
    )

    def __init__(self, root: Path) -> None:
        if root.is_symlink():
            raise GovernanceSourceError("real factory root must not be a symlink")
        self._root = root.resolve(strict=True)
        if not self._root.is_dir():
            raise GovernanceSourceError("real factory root must be a directory")

    def inspect(self) -> RealFactoryInventory:
        manifest = self._load_toml(self.FACTORY_MANIFEST)
        catalog = self._load_toml(self.PROJECT_CATALOG)
        factory_id = self._required_string(manifest, "id", self.FACTORY_MANIFEST)
        factory_schema = self._required_string(manifest, "schema", self.FACTORY_MANIFEST)
        schema_version = catalog.get("schema_version")
        if not isinstance(schema_version, int) or isinstance(schema_version, bool):
            raise GovernanceSourceError("factory catalog schema_version must be an integer")
        projects = catalog.get("projects")
        if not isinstance(projects, list):
            raise GovernanceSourceError("factory catalog projects must be an array")

        adoption: Counter[str] = Counter()
        portfolio: Counter[str] = Counter()
        for index, project in enumerate(projects):
            if not isinstance(project, dict):
                raise GovernanceSourceError(f"catalog project {index} must be a table")
            self._required_string(project, "id", self.PROJECT_CATALOG)
            try:
                validate_relative_path(self._required_string(project, "path", self.PROJECT_CATALOG))
            except UnsafePathError as exc:
                raise GovernanceSourceError(f"catalog project {index} has an unsafe path") from exc
            adoption[self._required_string(project, "adoption", self.PROJECT_CATALOG)] += 1
            portfolio[self._required_string(project, "portfolio", self.PROJECT_CATALOG)] += 1

        sources = (
            FactorySourceInventory(
                source="project_catalog",
                readiness=SourceReadiness.AVAILABLE,
                normative=True,
                relative_location=self.PROJECT_CATALOG,
                reason="Machine-readable application inventory and Golden Path adoption status.",
            ),
            *tuple(self._fixed_source(item) for item in self.EXISTING_TOOL_SOURCES),
            *tuple(
                FactorySourceInventory(
                    source=name,
                    readiness=SourceReadiness.MISSING,
                    normative=True,
                    relative_location=None,
                    reason=reason,
                )
                for name, reason in self.UNIMPLEMENTED_CONTRACTS
            ),
        )
        required = {
            "project_catalog",
            "capability_registry",
            "governance_policies",
            "authority_registry",
            "permit_registry",
        }
        ready = all(
            source.readiness is SourceReadiness.AVAILABLE
            for source in sources
            if source.source in required
        )
        return RealFactoryInventory(
            factory_id=factory_id,
            factory_schema=factory_schema,
            catalog_schema_version=schema_version,
            project_count=len(projects),
            adoption_counts=dict(sorted(adoption.items())),
            portfolio_counts=dict(sorted(portfolio.items())),
            sources=sources,
            ready_for_governance_evaluation=ready,
            privacy_boundary=(
                "Fixed factory metadata only; no application files, data, credentials, logs, or secrets scanned."
            ),
        )

    def _fixed_source(
        self,
        definition: tuple[str, str, SourceReadiness, bool, str],
    ) -> FactorySourceInventory:
        name, relative, present_readiness, normative, reason = definition
        path = self._root / relative
        readiness = (
            present_readiness
            if path.is_file() and not path.is_symlink()
            else SourceReadiness.MISSING
        )
        return FactorySourceInventory(
            source=name,
            readiness=readiness,
            normative=normative,
            relative_location=relative,
            reason=reason
            if readiness is not SourceReadiness.MISSING
            else "Declared source is absent.",
        )

    def _load_toml(self, relative: str) -> dict[str, Any]:
        path = self._root / relative
        if path.is_symlink():
            raise GovernanceSourceError(f"factory metadata must not be a symlink: {relative}")
        try:
            resolved = path.resolve(strict=True)
            resolved.relative_to(self._root)
        except (FileNotFoundError, ValueError) as exc:
            raise GovernanceSourceError(
                f"factory metadata is missing or escapes root: {relative}"
            ) from exc
        if not resolved.is_file() or resolved.stat().st_size > MAX_FACTORY_FILE_BYTES:
            raise GovernanceSourceError(f"factory metadata is invalid or too large: {relative}")
        try:
            with resolved.open("rb") as stream:
                payload = tomllib.load(stream)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            raise GovernanceSourceError(f"cannot parse factory metadata {relative}: {exc}") from exc
        if not isinstance(payload, dict):
            raise GovernanceSourceError(f"factory metadata root must be a table: {relative}")
        return payload

    @staticmethod
    def _required_string(payload: dict[str, Any], field: str, source: str) -> str:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            raise GovernanceSourceError(f"{source} requires a non-empty {field}")
        return value.strip()
