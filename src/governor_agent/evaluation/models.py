"""Schema-validated evaluation inputs, case results, and aggregate metrics."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from governor_agent.domain import DecisionStatus
from governor_agent.domain.paths import validate_relative_path

MODEL_CONFIG = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class EvaluationCase(BaseModel):
    model_config = MODEL_CONFIG

    id: str = Field(min_length=1)
    request_path: str = Field(min_length=1)
    expected_status: DecisionStatus
    human_decision_expected: bool
    validators_expected: bool
    required_policy_ids: frozenset[str] = Field(default_factory=frozenset)
    required_evidence_types: frozenset[str] = Field(default_factory=frozenset)
    expected_violation_code: str | None = None

    @field_validator("request_path")
    @classmethod
    def validate_request_path(cls, value: str) -> str:
        return validate_relative_path(value)


class EvaluationSuite(BaseModel):
    model_config = MODEL_CONFIG

    id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    cases: tuple[EvaluationCase, ...] = Field(min_length=1)


class EvaluationCaseResult(BaseModel):
    model_config = MODEL_CONFIG

    case_id: str
    expected_status: DecisionStatus
    observed_status: DecisionStatus
    status_correct: bool
    tool_selection_correct: bool
    policy_grounded: bool
    evidence_complete: bool
    human_interruption_correct: bool
    validator_behavior_correct: bool
    violation_correct: bool
    hallucinated_policy_ids: tuple[str, ...]
    passed: bool


class EvaluationMetrics(BaseModel):
    model_config = MODEL_CONFIG

    total_cases: int = Field(ge=1)
    passed_cases: int = Field(ge=0)
    decision_accuracy: float = Field(ge=0, le=1)
    tool_selection_accuracy: float = Field(ge=0, le=1)
    escalation_accuracy: float = Field(ge=0, le=1)
    policy_grounding_rate: float = Field(ge=0, le=1)
    evidence_completeness_rate: float = Field(ge=0, le=1)
    false_allow_rate: float = Field(ge=0, le=1)
    false_deny_rate: float = Field(ge=0, le=1)
    hallucinated_policy_rate: float = Field(ge=0, le=1)
    unnecessary_human_interruption_rate: float = Field(ge=0, le=1)


class EvaluationReport(BaseModel):
    model_config = MODEL_CONFIG

    evaluation_id: str = Field(pattern=r"^eval-[0-9a-f]{32}$")
    suite_id: str
    suite_version: str
    model_id: str
    timestamp: datetime
    cases: tuple[EvaluationCaseResult, ...]
    metrics: EvaluationMetrics
