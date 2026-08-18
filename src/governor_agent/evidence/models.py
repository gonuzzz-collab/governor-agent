"""Separate local raw evidence from externally safe structured evidence."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    StringConstraints,
    field_validator,
    model_validator,
)

from governor_agent.domain import EvidenceKind
from governor_agent.domain.models import utc_now

MODEL_CONFIG = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)
ShortText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=2_000),
]
Identifier = Annotated[
    str,
    StringConstraints(pattern=r"^[a-z][a-z0-9_]{0,63}$"),
]


class InformationClassification(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    SECRET = "SECRET"


class SourceRole(str, Enum):
    NORMATIVE = "NORMATIVE"
    DESCRIPTIVE = "DESCRIPTIVE"


class TrustLevel(str, Enum):
    TRUSTED_GOVERNANCE = "TRUSTED_GOVERNANCE"
    TRUSTED_VALIDATOR = "TRUSTED_VALIDATOR"
    OBSERVED_SOURCE = "OBSERVED_SOURCE"
    UNTRUSTED_REPOSITORY_CONTENT = "UNTRUSTED_REPOSITORY_CONTENT"
    MODEL_GENERATED = "MODEL_GENERATED"
    HUMAN_CONFIRMED = "HUMAN_CONFIRMED"


class FactValueKind(str, Enum):
    BOOLEAN = "BOOLEAN"
    COUNT = "COUNT"
    ENUM = "ENUM"
    HASH = "HASH"
    IDENTIFIER = "IDENTIFIER"
    PATH = "PATH"
    FREE_TEXT = "FREE_TEXT"
    CODE = "CODE"


class ExternalProcessingAction(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_SANITIZED = "ALLOW_SANITIZED"
    ALLOW_METADATA_ONLY = "ALLOW_METADATA_ONLY"
    BLOCK_EXTERNAL_EXPOSURE = "BLOCK_EXTERNAL_EXPOSURE"


class RawFact(BaseModel):
    """Local-only fact. Its value is masked by default in representations and dumps."""

    model_config = MODEL_CONFIG

    name: Identifier
    value: SecretStr = Field(min_length=1, max_length=100_000)
    value_kind: FactValueKind
    necessary: bool = True


class RawEvidence(BaseModel):
    """Local-only evidence that must never cross an intelligence-provider boundary."""

    model_config = MODEL_CONFIG

    schema_version: Literal["governor.raw-evidence.v1"] = "governor.raw-evidence.v1"
    evidence_id: str = Field(pattern=r"^raw-[a-z0-9][a-z0-9-]{2,63}$")
    source_type: Identifier
    classification: InformationClassification
    kind: EvidenceKind
    trust_level: TrustLevel
    source_role: SourceRole
    local_project: SecretStr = Field(min_length=1, max_length=500)
    local_component: SecretStr | None = Field(default=None, max_length=500)
    event_type: Identifier
    change_type: Identifier | None = None
    source_path: Path | None = None
    facts: tuple[RawFact, ...] = Field(min_length=1, max_length=64)
    applicable_policy_refs: tuple[ShortText, ...] = Field(default=(), max_length=32)
    timestamp: datetime = Field(default_factory=utc_now)

    @field_validator("timestamp")
    @classmethod
    def aware_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("timestamp must include a timezone")
        return value

    @model_validator(mode="after")
    def authority_bearing_kinds_require_authorized_provenance(self) -> "RawEvidence":
        if self.kind is EvidenceKind.POLICY and (
            self.source_role is not SourceRole.NORMATIVE
            or self.trust_level not in {TrustLevel.TRUSTED_GOVERNANCE, TrustLevel.HUMAN_CONFIRMED}
        ):
            raise ValueError("policy evidence requires authorized normative provenance")
        if self.kind is EvidenceKind.HUMAN_DECISION and (
            self.trust_level is not TrustLevel.HUMAN_CONFIRMED
        ):
            raise ValueError("human decisions require human-confirmed provenance")
        if self.kind in {EvidenceKind.MODEL_ADVISORY, EvidenceKind.MODEL_INTERPRETATION} and (
            self.trust_level is not TrustLevel.MODEL_GENERATED
            or self.source_role is not SourceRole.DESCRIPTIVE
        ):
            raise ValueError("model evidence must remain descriptive and model-generated")
        return self


class EvidenceStatement(BaseModel):
    model_config = MODEL_CONFIG

    statement_id: Identifier
    kind: EvidenceKind
    name: Identifier
    value: ShortText
    value_kind: FactValueKind
    trust_level: TrustLevel


class EvidenceDigest(BaseModel):
    model_config = MODEL_CONFIG

    subject: Identifier
    algorithm: Literal["sha256"] = "sha256"
    value: str = Field(pattern=r"^[0-9a-f]{64}$")


class RedactionRecord(BaseModel):
    model_config = MODEL_CONFIG

    field: Identifier
    reason: Identifier


class EvidenceProvenance(BaseModel):
    model_config = MODEL_CONFIG

    source_type: Identifier
    source_role: SourceRole
    trust_level: TrustLevel
    logical_source: str = Field(pattern=r"^factory://[^\s]+$", max_length=1_000)


class SanitizedEvidence(BaseModel):
    """Structured evidence safe to inspect; policy still controls external processing."""

    model_config = MODEL_CONFIG

    schema_version: Literal["governor.sanitized-evidence.v1"] = "governor.sanitized-evidence.v1"
    evidence_id: str = Field(pattern=r"^ev-[a-z0-9][a-z0-9-]{2,63}$")
    classification: InformationClassification
    project_alias: str = Field(pattern=r"^(PUBLIC_[A-Z0-9_]{1,80}|PROJECT_[0-9A-F]{12})$")
    component_alias: str | None = Field(
        default=None, pattern=r"^(PUBLIC_[A-Z0-9_]{1,80}|COMPONENT_[0-9A-F]{12})$"
    )
    event_type: Identifier
    change_type: Identifier | None = None
    statements: tuple[EvidenceStatement, ...] = Field(default=(), max_length=64)
    applicable_policy_refs: tuple[ShortText, ...] = Field(default=(), max_length=32)
    hashes: tuple[EvidenceDigest, ...] = Field(default=(), max_length=64)
    redactions: tuple[RedactionRecord, ...] = Field(default=(), max_length=128)
    provenance: EvidenceProvenance
    external_processing_allowed: bool
    external_processing_action: ExternalProcessingAction
    timestamp: datetime

    @field_validator("timestamp")
    @classmethod
    def aware_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("timestamp must include a timezone")
        return value

    @model_validator(mode="after")
    def external_policy_fields_are_consistent(self) -> "SanitizedEvidence":
        expected = {
            InformationClassification.PUBLIC: ExternalProcessingAction.ALLOW,
            InformationClassification.INTERNAL: ExternalProcessingAction.ALLOW_SANITIZED,
            InformationClassification.CONFIDENTIAL: ExternalProcessingAction.ALLOW_METADATA_ONLY,
            InformationClassification.SECRET: ExternalProcessingAction.BLOCK_EXTERNAL_EXPOSURE,
        }[self.classification]
        if self.external_processing_action is not expected:
            raise ValueError("external-processing action must match classification")
        expected_allowed = (
            self.external_processing_action is not ExternalProcessingAction.BLOCK_EXTERNAL_EXPOSURE
        )
        if self.external_processing_allowed is not expected_allowed:
            raise ValueError("external-processing permission must match action")
        for statement in self.statements:
            if statement.kind is EvidenceKind.POLICY and (
                self.provenance.source_role is not SourceRole.NORMATIVE
                or statement.trust_level
                not in {TrustLevel.TRUSTED_GOVERNANCE, TrustLevel.HUMAN_CONFIRMED}
            ):
                raise ValueError("sanitized policy requires authorized normative provenance")
        return self


class SanitizationAudit(BaseModel):
    """Redacted processing evidence; never contains raw values or local identifiers."""

    model_config = MODEL_CONFIG

    raw_evidence_id: str
    sanitized_evidence_id: str
    original_classification: InformationClassification
    effective_classification: InformationClassification
    raw_fact_names: tuple[Identifier, ...]
    retained_fact_names: tuple[Identifier, ...]
    removed_fact_names: tuple[Identifier, ...]
    secret_detected: bool
    detector_ids: tuple[Identifier, ...]
    external_processing_action: ExternalProcessingAction
    external_processing_reason: ShortText
    external_payload_digest: str | None = Field(default=None, pattern=r"^sha256:[0-9a-f]{64}$")


class SanitizationResult(BaseModel):
    model_config = MODEL_CONFIG

    evidence: SanitizedEvidence
    audit: SanitizationAudit
