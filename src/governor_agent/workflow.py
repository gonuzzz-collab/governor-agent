"""End-to-end local governance workflow."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from governor_agent.adapters import GovernanceSource
from governor_agent.audit import AuditRecord, AuditStore
from governor_agent.domain import (
    ChangeRequest,
    DecisionStatus,
    EvaluationContext,
    GovernanceDecision,
    GovernanceEvaluator,
    ValidationResult,
)
from governor_agent.validation import ApprovedValidatorRunner


@dataclass(frozen=True)
class WorkflowResult:
    decision: GovernanceDecision
    validations: tuple[ValidationResult, ...]
    audit_record: AuditRecord
    audit_path: Path


class GovernorWorkflow:
    """Resolve governance, run approved validators, decide, and record evidence."""

    def __init__(self, source: GovernanceSource, audit_store: AuditStore) -> None:
        self._source = source
        self._audit_store = audit_store
        self._evaluator = GovernanceEvaluator()
        self._validators = ApprovedValidatorRunner(source.project_root)

    def evaluate(self, request: ChangeRequest) -> WorkflowResult:
        self._source.get_golden_path()
        context = EvaluationContext(
            request=request,
            capability=self._source.get_capability(request.capability),
            authority=self._source.get_authority(request.actor),
            permit=self._source.get_permit(request.id),
            policies=self._source.get_policies(request),
        )
        preliminary = self._evaluator.evaluate(context)
        validations: tuple[ValidationResult, ...] = ()

        if self._requires_validators(preliminary):
            validations = tuple(
                self._validators.run(self._source.get_validator(validator_id), request)
                for validator_id in preliminary.validations_required
            )
            context = context.model_copy(update={"validations": validations})
            decision = self._evaluator.evaluate(context)
        else:
            decision = preliminary

        record, path = self._audit_store.record(request, decision, validations)
        return WorkflowResult(decision, validations, record, path)

    @staticmethod
    def _requires_validators(decision: GovernanceDecision) -> bool:
        return (
            decision.status is DecisionStatus.INCOMPLETE_EVIDENCE
            and bool(decision.validations_required)
            and all(violation.code == "missing_validator" for violation in decision.violations)
        )
