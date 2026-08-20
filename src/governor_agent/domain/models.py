"""Schema-validated governance domain models.

These models are authority-bearing data structures. Free-form model output never replaces them.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from governor_agent.domain.paths import validate_relative_path


def utc_now() -> datetime:
    """Return an aware UTC timestamp."""

    return datetime.now(timezone.utc)


class ValueEnum(str, Enum):
    """String enum with stable JSON values."""


class DecisionStatus(ValueEnum):
    ALLOW = "ALLOW"
    ALLOW_WITH_CONDITIONS = "ALLOW_WITH_CONDITIONS"
    DENY = "DENY"
    ESCALATE = "ESCALATE"
    INCOMPLETE_EVIDENCE = "INCOMPLETE_EVIDENCE"
    VALIDATION_FAILED = "VALIDATION_FAILED"


class EvidenceKind(ValueEnum):
    FACT = "FACT"
    INFERENCE = "INFERENCE"
    POLICY = "POLICY"
    MODEL_INTERPRETATION = "MODEL_INTERPRETATION"
    MODEL_ADVISORY = "MODEL_ADVISORY"
    HUMAN_DECISION = "HUMAN_DECISION"


class EvidenceStatus(ValueEnum):
    OK = "ok"
    WARN = "warn"
    FAIL = "fail"
    MISSING = "missing"


class RiskLevel(ValueEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PermitStatus(ValueEnum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    CLOSED = "CLOSED"


class Lifecycle(ValueEnum):
    EXPERIMENTAL = "experimental"
    SHARED = "shared"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class PolicyKind(ValueEnum):
    FORBIDDEN_PATH = "forbidden_path"
    REQUIRED_VALIDATOR = "required_validator"
    PERSISTENCE_OWNERSHIP = "persistence_ownership"


class ValidationStatus(ValueEnum):
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"


MODEL_CONFIG = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class ChangeRequest(BaseModel):
    model_config = MODEL_CONFIG

    id: str = Field(min_length=1)
    project: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    actor: str = Field(min_length=1)
    capability: str = Field(min_length=1)
    action: str = Field(default="change", min_length=1)
    requested_scope: tuple[str, ...] = Field(min_length=1)
    files: tuple[str, ...] = Field(min_length=1)
    effects: frozenset[str] = Field(default_factory=frozenset)
    environment: str = Field(default="local", min_length=1)
    risk_level: RiskLevel = RiskLevel.LOW
    expected_evidence: frozenset[str] = Field(default_factory=frozenset)

    @field_validator("requested_scope")
    @classmethod
    def validate_scope(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(validate_relative_path(value, allow_glob=True) for value in values)

    @field_validator("files")
    @classmethod
    def validate_files(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(validate_relative_path(value) for value in values)

    @model_validator(mode="after")
    def unique_files(self) -> "ChangeRequest":
        if len(set(self.files)) != len(self.files):
            raise ValueError("files must be unique")
        return self


class Capability(BaseModel):
    model_config = MODEL_CONFIG

    id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    lifecycle: Lifecycle
    allowed_actions: frozenset[str] = Field(min_length=1)
    validators: tuple[str, ...] = ()
    evidence_required: frozenset[str] = Field(default_factory=frozenset)


class CapabilityRegistry(BaseModel):
    """Versioned, authority-bearing capabilities from one explicit normative source."""

    model_config = MODEL_CONFIG

    schema_version: Literal["governor.capability-registry.v1"]
    capabilities: tuple[Capability, ...] = Field(min_length=1, max_length=256)

    @model_validator(mode="after")
    def unique_capability_ids(self) -> "CapabilityRegistry":
        capability_ids = tuple(capability.id for capability in self.capabilities)
        if len(set(capability_ids)) != len(capability_ids):
            raise ValueError("capability registry must not contain duplicate capability IDs")
        return self


class AuthorityGrant(BaseModel):
    model_config = MODEL_CONFIG

    actor: str = Field(min_length=1)
    allowed_actions: frozenset[str] = Field(default_factory=frozenset)
    allowed_paths: tuple[str, ...] = ()
    environments: frozenset[str] = Field(default_factory=lambda: frozenset({"local"}))
    expires_at: datetime | None = None

    @field_validator("allowed_paths")
    @classmethod
    def validate_paths(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(validate_relative_path(value, allow_glob=True) for value in values)

    @field_validator("expires_at")
    @classmethod
    def aware_expiry(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo is None:
            raise ValueError("expires_at must include a timezone")
        return value


class AuthorityRegistry(BaseModel):
    """Versioned, authority-bearing grants from one explicit normative source."""

    model_config = MODEL_CONFIG

    schema_version: Literal["governor.authority-registry.v1"]
    authorities: tuple[AuthorityGrant, ...] = Field(min_length=1, max_length=256)

    @model_validator(mode="after")
    def unique_actors(self) -> "AuthorityRegistry":
        actors = tuple(authority.actor for authority in self.authorities)
        if len(set(actors)) != len(actors):
            raise ValueError("authority registry must not contain duplicate actors")
        return self


class ChangePermit(BaseModel):
    model_config = MODEL_CONFIG

    permit_id: str = Field(min_length=1)
    request_id: str = Field(min_length=1)
    capability: str = Field(min_length=1)
    actor: str = Field(min_length=1)
    allowed_actions: frozenset[str] = Field(default_factory=frozenset)
    allowed_paths: tuple[str, ...] = ()
    forbidden_actions: frozenset[str] = Field(default_factory=frozenset)
    environment: str = Field(min_length=1)
    validators: tuple[str, ...] = ()
    evidence_required: frozenset[str] = Field(default_factory=frozenset)
    expires_at: datetime | None = None
    rollback: str = Field(min_length=1)
    status: PermitStatus = PermitStatus.ACTIVE

    @field_validator("allowed_paths")
    @classmethod
    def validate_paths(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(validate_relative_path(value, allow_glob=True) for value in values)

    @field_validator("expires_at")
    @classmethod
    def aware_expiry(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo is None:
            raise ValueError("expires_at must include a timezone")
        return value


class PermitRegistry(BaseModel):
    """Versioned permits from one explicit normative source."""

    model_config = MODEL_CONFIG

    schema_version: Literal["governor.permit-registry.v1"]
    permits: tuple[ChangePermit, ...] = Field(default=(), max_length=512)

    @model_validator(mode="after")
    def unique_permit_and_request_ids(self) -> "PermitRegistry":
        permit_ids = tuple(permit.permit_id for permit in self.permits)
        request_ids = tuple(permit.request_id for permit in self.permits)
        if len(set(permit_ids)) != len(permit_ids):
            raise ValueError("permit registry must not contain duplicate permit IDs")
        if len(set(request_ids)) != len(request_ids):
            raise ValueError("permit registry must not contain duplicate request IDs")
        return self


class Policy(BaseModel):
    model_config = MODEL_CONFIG

    id: str = Field(min_length=1)
    kind: PolicyKind
    description: str = Field(min_length=1)
    paths: tuple[str, ...] = ()
    required_validator: str | None = None
    trigger_effect: str | None = None
    existing_source: str | None = None
    options: tuple[str, ...] = ()

    @field_validator("paths")
    @classmethod
    def validate_paths(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(validate_relative_path(value, allow_glob=True) for value in values)

    @model_validator(mode="after")
    def validate_kind_contract(self) -> "Policy":
        if self.kind is PolicyKind.FORBIDDEN_PATH and not self.paths:
            raise ValueError("forbidden_path policy requires paths")
        if self.kind is PolicyKind.REQUIRED_VALIDATOR and not self.required_validator:
            raise ValueError("required_validator policy requires required_validator")
        if self.kind is PolicyKind.PERSISTENCE_OWNERSHIP:
            if not self.trigger_effect or not self.existing_source or len(self.options) < 2:
                raise ValueError(
                    "persistence_ownership policy requires trigger_effect, existing_source, and options"
                )
        return self


class PolicyRegistry(BaseModel):
    """Versioned policies from one explicit normative source."""

    model_config = MODEL_CONFIG

    schema_version: Literal["governor.policy-registry.v1"]
    policies: tuple[Policy, ...] = Field(min_length=1, max_length=512)

    @model_validator(mode="after")
    def unique_policy_ids(self) -> "PolicyRegistry":
        policy_ids = tuple(policy.id for policy in self.policies)
        if len(set(policy_ids)) != len(policy_ids):
            raise ValueError("policy registry must not contain duplicate policy IDs")
        return self


class EvidenceItem(BaseModel):
    model_config = MODEL_CONFIG

    evidence_id: str = Field(min_length=1)
    kind: EvidenceKind
    source: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    status: EvidenceStatus
    detail: str = Field(min_length=1)
    evidence_types: frozenset[str] = Field(default_factory=frozenset)
    timestamp: datetime = Field(default_factory=utc_now)
    digest: str | None = None

    @field_validator("timestamp")
    @classmethod
    def aware_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("timestamp must include a timezone")
        return value


class ValidationResult(BaseModel):
    model_config = MODEL_CONFIG

    validator_id: str = Field(min_length=1)
    status: ValidationStatus
    summary: str = Field(min_length=1)
    evidence_types: frozenset[str] = Field(default_factory=frozenset)


class Violation(BaseModel):
    model_config = MODEL_CONFIG

    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    policy_id: str | None = None
    path: str | None = None


class HumanDecisionRequest(BaseModel):
    model_config = MODEL_CONFIG

    question: str = Field(min_length=1)
    context: str = Field(min_length=1)
    options: tuple[str, ...] = Field(min_length=2)
    risks: tuple[str, ...] = Field(min_length=1)


class EvaluationContext(BaseModel):
    model_config = MODEL_CONFIG

    request: ChangeRequest
    capability: Capability
    authority: AuthorityGrant
    permit: ChangePermit | None
    policies: tuple[Policy, ...]
    validations: tuple[ValidationResult, ...] = ()
    evidence: tuple[EvidenceItem, ...] = ()


class GovernanceDecision(BaseModel):
    model_config = MODEL_CONFIG

    decision_id: str = Field(pattern=r"^gov-[0-9a-f]{16}$")
    project: str
    request_id: str
    status: DecisionStatus
    risk_level: RiskLevel
    authority_required: str
    authority_available: tuple[str, ...]
    policies_applied: tuple[str, ...]
    capabilities_required: tuple[str, ...]
    evidence: tuple[EvidenceItem, ...]
    violations: tuple[Violation, ...]
    allowed_scope: tuple[str, ...]
    prohibited_scope: tuple[str, ...]
    validations_required: tuple[str, ...]
    automatic_actions: tuple[str, ...]
    human_decisions: tuple[HumanDecisionRequest, ...]
    explanation: str = Field(min_length=1)
    timestamp: datetime = Field(default_factory=utc_now)

    @field_validator("timestamp")
    @classmethod
    def aware_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("timestamp must include a timezone")
        return value

    def as_jsonable(self) -> dict[str, Any]:
        """Return a stable JSON-compatible representation."""

        return self.model_dump(mode="json")
