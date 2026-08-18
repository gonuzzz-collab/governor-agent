"""Privacy-preserving, read-only inventory adapter for the real GoNucleo factory.

This adapter deliberately does not implement GovernanceSource. The current factory exposes a
machine-readable project catalog, but not complete policy, capability, authority, and permit
registries with the Governor contracts. Reporting that gap is safer than inventing an integration.
"""

from __future__ import annotations

import tomllib
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from governor_agent.adapters.contracts import GovernanceSourceError
from governor_agent.domain import EvidenceKind
from governor_agent.domain.paths import UnsafePathError, validate_relative_path
from governor_agent.evidence import (
    FactoryEvidenceCollection,
    FactValueKind,
    InformationClassification,
    RawEvidence,
    RawFact,
    SourceRole,
    TrustLevel,
)

MAX_FACTORY_FILE_BYTES = 1_000_000


class SourceReadiness(str, Enum):
    AVAILABLE = "available"
    PARTIAL = "partial"
    MISSING = "missing"


class FactorySourceFormat(str, Enum):
    TOML = "toml"
    JSON_SCHEMA = "json-schema"
    EXECUTABLE = "executable"
    MARKDOWN = "markdown"
    ABSENT = "absent"


class FactorySourceInventory(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    source: str
    readiness: SourceReadiness
    normative: bool
    relative_location: str | None
    format: FactorySourceFormat
    machine_readable: bool
    source_role: SourceRole
    classification: InformationClassification
    adapter_needed: bool
    sanitization_needed: bool
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


@dataclass(frozen=True)
class FactorySourceDefinition:
    source: str
    relative_location: str | None
    readiness_when_present: SourceReadiness
    normative: bool
    format: FactorySourceFormat
    machine_readable: bool
    source_role: SourceRole
    classification: InformationClassification
    adapter_needed: bool
    sanitization_needed: bool
    reason: str


class GoNucleoFactoryInventoryAdapter:
    """Inspect only fixed factory metadata paths; never recurse through application data."""

    FACTORY_MANIFEST = ".gonucleo-factory.toml"
    PROJECT_CATALOG = ".skills/factory-catalog.toml"
    FIXED_SOURCES = (
        FactorySourceDefinition(
            source="factory_manifest",
            relative_location=FACTORY_MANIFEST,
            readiness_when_present=SourceReadiness.AVAILABLE,
            normative=True,
            format=FactorySourceFormat.TOML,
            machine_readable=True,
            source_role=SourceRole.NORMATIVE,
            classification=InformationClassification.INTERNAL,
            adapter_needed=False,
            sanitization_needed=True,
            reason="Machine-readable factory identity and local automation contract.",
        ),
        FactorySourceDefinition(
            source="project_catalog",
            relative_location=PROJECT_CATALOG,
            readiness_when_present=SourceReadiness.AVAILABLE,
            normative=True,
            format=FactorySourceFormat.TOML,
            machine_readable=True,
            source_role=SourceRole.NORMATIVE,
            classification=InformationClassification.INTERNAL,
            adapter_needed=False,
            sanitization_needed=True,
            reason="Machine-readable application inventory and Golden Path adoption status.",
        ),
        FactorySourceDefinition(
            source="golden_path_tool",
            relative_location=".skills/project-golden-path",
            readiness_when_present=SourceReadiness.PARTIAL,
            normative=True,
            format=FactorySourceFormat.EXECUTABLE,
            machine_readable=False,
            source_role=SourceRole.NORMATIVE,
            classification=InformationClassification.INTERNAL,
            adapter_needed=True,
            sanitization_needed=True,
            reason="Normative scaffolding tool, not a complete machine-readable change-policy source.",
        ),
        FactorySourceDefinition(
            source="factory_status_tool",
            relative_location=".skills/factory-status",
            readiness_when_present=SourceReadiness.PARTIAL,
            normative=False,
            format=FactorySourceFormat.EXECUTABLE,
            machine_readable=True,
            source_role=SourceRole.DESCRIPTIVE,
            classification=InformationClassification.INTERNAL,
            adapter_needed=True,
            sanitization_needed=True,
            reason="Derived project-state report from the catalog and project manifests.",
        ),
        FactorySourceDefinition(
            source="governance_policies",
            relative_location="AGENTS.md",
            readiness_when_present=SourceReadiness.PARTIAL,
            normative=True,
            format=FactorySourceFormat.MARKDOWN,
            machine_readable=False,
            source_role=SourceRole.NORMATIVE,
            classification=InformationClassification.INTERNAL,
            adapter_needed=True,
            sanitization_needed=True,
            reason="Authorized agent rules exist, but not as a complete typed Governor policy registry.",
        ),
        FactorySourceDefinition(
            source="capability_governance_analysis",
            relative_location="docs/fabrica_aplicaciones/GOBERNANZA_CAPACIDADES_CORTE0_2026-08-15.md",
            readiness_when_present=SourceReadiness.PARTIAL,
            normative=False,
            format=FactorySourceFormat.MARKDOWN,
            machine_readable=False,
            source_role=SourceRole.DESCRIPTIVE,
            classification=InformationClassification.CONFIDENTIAL,
            adapter_needed=True,
            sanitization_needed=True,
            reason="Capability governance is an unclosed analysis, not an authority-bearing registry.",
        ),
        FactorySourceDefinition(
            source="change_permit_tool",
            relative_location=".skills/change-permit",
            readiness_when_present=SourceReadiness.PARTIAL,
            normative=True,
            format=FactorySourceFormat.EXECUTABLE,
            machine_readable=True,
            source_role=SourceRole.NORMATIVE,
            classification=InformationClassification.INTERNAL,
            adapter_needed=True,
            sanitization_needed=True,
            reason="Report-only workflow exists without a persistent schema-compatible permit registry.",
        ),
        FactorySourceDefinition(
            source="safety_gate_tool",
            relative_location=".skills/safety-gate",
            readiness_when_present=SourceReadiness.PARTIAL,
            normative=True,
            format=FactorySourceFormat.EXECUTABLE,
            machine_readable=True,
            source_role=SourceRole.NORMATIVE,
            classification=InformationClassification.INTERNAL,
            adapter_needed=True,
            sanitization_needed=True,
            reason="Deterministic command-risk gate, not a general actor-authority registry.",
        ),
        FactorySourceDefinition(
            source="validator_registry",
            relative_location=FACTORY_MANIFEST,
            readiness_when_present=SourceReadiness.PARTIAL,
            normative=True,
            format=FactorySourceFormat.TOML,
            machine_readable=True,
            source_role=SourceRole.NORMATIVE,
            classification=InformationClassification.INTERNAL,
            adapter_needed=True,
            sanitization_needed=True,
            reason="Automation commands are declared, but approved validators are not a standalone registry.",
        ),
        FactorySourceDefinition(
            source="evidence_contract",
            relative_location="docs/fabrica_aplicaciones/schemas/gonucleo.evidence.v1.schema.json",
            readiness_when_present=SourceReadiness.AVAILABLE,
            normative=True,
            format=FactorySourceFormat.JSON_SCHEMA,
            machine_readable=True,
            source_role=SourceRole.NORMATIVE,
            classification=InformationClassification.INTERNAL,
            adapter_needed=True,
            sanitization_needed=True,
            reason="Canonical machine-readable evidence interchange contract.",
        ),
        FactorySourceDefinition(
            source="architecture",
            relative_location="project_memory/ARCHITECTURE.md",
            readiness_when_present=SourceReadiness.PARTIAL,
            normative=False,
            format=FactorySourceFormat.MARKDOWN,
            machine_readable=False,
            source_role=SourceRole.DESCRIPTIVE,
            classification=InformationClassification.CONFIDENTIAL,
            adapter_needed=True,
            sanitization_needed=True,
            reason="Narrative architecture context; it cannot establish policy by itself.",
        ),
        FactorySourceDefinition(
            source="capability_registry",
            relative_location=None,
            readiness_when_present=SourceReadiness.MISSING,
            normative=True,
            format=FactorySourceFormat.ABSENT,
            machine_readable=False,
            source_role=SourceRole.NORMATIVE,
            classification=InformationClassification.CONFIDENTIAL,
            adapter_needed=True,
            sanitization_needed=True,
            reason="No machine-readable authority-bearing capability registry is defined.",
        ),
        FactorySourceDefinition(
            source="authority_registry",
            relative_location=None,
            readiness_when_present=SourceReadiness.MISSING,
            normative=True,
            format=FactorySourceFormat.ABSENT,
            machine_readable=False,
            source_role=SourceRole.NORMATIVE,
            classification=InformationClassification.CONFIDENTIAL,
            adapter_needed=True,
            sanitization_needed=True,
            reason="No machine-readable actor-authority registry is defined.",
        ),
        FactorySourceDefinition(
            source="permit_registry",
            relative_location=None,
            readiness_when_present=SourceReadiness.MISSING,
            normative=True,
            format=FactorySourceFormat.ABSENT,
            machine_readable=False,
            source_role=SourceRole.NORMATIVE,
            classification=InformationClassification.CONFIDENTIAL,
            adapter_needed=True,
            sanitization_needed=True,
            reason="No persistent schema-compatible Change Permit registry is defined.",
        ),
    )

    def __init__(self, root: Path) -> None:
        if root.is_symlink():
            raise GovernanceSourceError("real factory root must not be a symlink")
        self._root = root.resolve(strict=True)
        if not self._root.is_dir():
            raise GovernanceSourceError("real factory root must be a directory")

    @property
    def factory_root(self) -> Path:
        return self._root

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

        sources = tuple(self._fixed_source(item) for item in self.FIXED_SOURCES)
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

    def collect_evidence(self) -> FactoryEvidenceCollection:
        """Extract only aggregate, typed facts from the fixed inventory allowlist."""

        inventory = self.inspect()
        missing = tuple(
            item.source
            for item in inventory.sources
            if item.normative and item.readiness is SourceReadiness.MISSING
        )
        partial = tuple(
            item.source
            for item in inventory.sources
            if item.normative and item.readiness is SourceReadiness.PARTIAL
        )
        facts = [
            RawFact(
                name="catalog_schema_version",
                value=str(inventory.catalog_schema_version),
                value_kind=FactValueKind.COUNT,
            ),
            RawFact(
                name="project_count",
                value=str(inventory.project_count),
                value_kind=FactValueKind.COUNT,
            ),
            RawFact(
                name="governance_ready",
                value=str(inventory.ready_for_governance_evaluation).lower(),
                value_kind=FactValueKind.BOOLEAN,
            ),
            RawFact(
                name="missing_contract_count",
                value=str(len(missing)),
                value_kind=FactValueKind.COUNT,
            ),
            RawFact(
                name="partial_contract_count",
                value=str(len(partial)),
                value_kind=FactValueKind.COUNT,
            ),
        ]
        for adoption, count in sorted(inventory.adoption_counts.items()):
            facts.append(
                RawFact(
                    name=f"adoption_{adoption.replace('-', '_')}",
                    value=str(count),
                    value_kind=FactValueKind.COUNT,
                )
            )
        for source in inventory.sources:
            facts.append(
                RawFact(
                    name=f"source_{source.source}",
                    value=source.readiness.value,
                    value_kind=FactValueKind.ENUM,
                )
            )
        raw = RawEvidence(
            evidence_id="raw-factory-readiness",
            source_type="factory_inventory",
            classification=InformationClassification.INTERNAL,
            kind=EvidenceKind.FACT,
            trust_level=TrustLevel.OBSERVED_SOURCE,
            source_role=SourceRole.DESCRIPTIVE,
            local_project=inventory.factory_id,
            local_component="governance-metadata",
            event_type="governance_readiness_observation",
            facts=tuple(facts),
            applicable_policy_refs=("fixed-source-allowlist", "read-only-evidence"),
        )
        return FactoryEvidenceCollection(
            evidence=(raw,),
            ready_for_governance_evaluation=inventory.ready_for_governance_evaluation,
            missing_contracts=missing,
            partial_contracts=partial,
        )

    def _fixed_source(
        self,
        definition: FactorySourceDefinition,
    ) -> FactorySourceInventory:
        relative = definition.relative_location
        readiness = definition.readiness_when_present
        if relative is not None:
            path = self._root / relative
            readiness = (
                definition.readiness_when_present
                if path.is_file() and not path.is_symlink()
                else SourceReadiness.MISSING
            )
        return FactorySourceInventory(
            source=definition.source,
            readiness=readiness,
            normative=definition.normative,
            relative_location=relative,
            format=definition.format,
            machine_readable=definition.machine_readable,
            source_role=definition.source_role,
            classification=definition.classification,
            adapter_needed=definition.adapter_needed,
            sanitization_needed=definition.sanitization_needed,
            reason=(
                definition.reason
                if readiness is not SourceReadiness.MISSING or relative is None
                else "Declared source is absent."
            ),
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


class RealFactoryAdapter(GoNucleoFactoryInventoryAdapter):
    """Canonical read-only adapter name; legacy inventory name remains compatible."""
