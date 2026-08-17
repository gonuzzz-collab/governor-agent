"""Run deterministic offline behavioral evaluations through the real Strands loop."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError

from governor_agent.adapters import SyntheticFactoryAdapter
from governor_agent.agent import GovernorAgentRunner
from governor_agent.audit import AuditStore
from governor_agent.domain import ChangeRequest, DecisionStatus
from governor_agent.evaluation.models import (
    EvaluationCase,
    EvaluationCaseResult,
    EvaluationMetrics,
    EvaluationReport,
    EvaluationSuite,
)

MAX_EVALUATION_FILE_BYTES = 1_000_000
EXPECTED_TOOL_TRACE = (
    "inspect_change_request",
    "inspect_governance",
    "evaluate_change_request",
    "AgentGovernanceReport",
)
ALLOW_STATUSES = {DecisionStatus.ALLOW, DecisionStatus.ALLOW_WITH_CONDITIONS}
DENY_STATUSES = {
    DecisionStatus.DENY,
    DecisionStatus.VALIDATION_FAILED,
    DecisionStatus.INCOMPLETE_EVIDENCE,
}


class EvaluationSourceError(RuntimeError):
    """Raised when the evaluation suite is unsafe or malformed."""


class AgentEvaluationRunner:
    """Measure safe autonomy and evidence-grounded agent behavior."""

    def __init__(self, factory_root: Path, audit_root: Path) -> None:
        self._factory_root = factory_root.resolve(strict=True)
        self._audit_root = audit_root

    def run(self, suite_path: Path) -> EvaluationReport:
        suite = self._load_suite(suite_path)
        results = tuple(self._run_case(case) for case in suite.cases)
        return EvaluationReport(
            evaluation_id=f"eval-{uuid.uuid4().hex}",
            suite_id=suite.id,
            suite_version=suite.version,
            model_id="governor-offline-deterministic",
            timestamp=datetime.now(timezone.utc),
            cases=results,
            metrics=self._metrics(suite, results),
        )

    def _run_case(self, case: EvaluationCase) -> EvaluationCaseResult:
        request_path = self._resolve_request(case.request_path)
        source = SyntheticFactoryAdapter(self._factory_root)
        runner = GovernorAgentRunner(source, AuditStore(self._audit_root), request_path)
        result = runner.run()
        decision = result.workflow.decision

        request = self._load_request(request_path)
        configured_policy_ids = {policy.id for policy in source.get_policies(request)}
        applied_policy_ids = set(decision.policies_applied)
        hallucinated = tuple(sorted(applied_policy_ids - configured_policy_ids))
        observed_evidence = {
            evidence_type for item in decision.evidence for evidence_type in item.evidence_types
        }
        observed_violations = {item.code for item in decision.violations}
        status_correct = decision.status is case.expected_status
        tool_selection_correct = result.tool_trace == EXPECTED_TOOL_TRACE
        policy_grounded = case.required_policy_ids <= applied_policy_ids and not hallucinated
        evidence_complete = case.required_evidence_types <= observed_evidence
        human_correct = bool(decision.human_decisions) is case.human_decision_expected
        validator_correct = bool(result.workflow.validations) is case.validators_expected
        violation_correct = (
            case.expected_violation_code is None
            or case.expected_violation_code in observed_violations
        )
        passed = all(
            (
                status_correct,
                tool_selection_correct,
                policy_grounded,
                evidence_complete,
                human_correct,
                validator_correct,
                violation_correct,
            )
        )
        return EvaluationCaseResult(
            case_id=case.id,
            expected_status=case.expected_status,
            observed_status=decision.status,
            status_correct=status_correct,
            tool_selection_correct=tool_selection_correct,
            policy_grounded=policy_grounded,
            evidence_complete=evidence_complete,
            human_interruption_correct=human_correct,
            validator_behavior_correct=validator_correct,
            violation_correct=violation_correct,
            hallucinated_policy_ids=hallucinated,
            passed=passed,
        )

    def _load_suite(self, path: Path) -> EvaluationSuite:
        if path.is_symlink():
            raise EvaluationSourceError("evaluation suite must not be a symlink")
        resolved = path.resolve(strict=True)
        if resolved.stat().st_size > MAX_EVALUATION_FILE_BYTES:
            raise EvaluationSourceError("evaluation suite exceeds size limit")
        try:
            with resolved.open("r", encoding="utf-8") as stream:
                return EvaluationSuite.model_validate(json.load(stream))
        except (OSError, UnicodeError, json.JSONDecodeError, ValidationError) as exc:
            raise EvaluationSourceError(f"invalid evaluation suite: {exc}") from exc

    def _resolve_request(self, relative: str) -> Path:
        candidate = self._factory_root / relative
        current = candidate
        while current != self._factory_root:
            if current.is_symlink():
                raise EvaluationSourceError(f"evaluation request contains a symlink: {relative}")
            current = current.parent
        resolved = candidate.resolve(strict=True)
        try:
            resolved.relative_to(self._factory_root)
        except ValueError as exc:
            raise EvaluationSourceError(f"evaluation request escapes factory: {relative}") from exc
        return resolved

    @staticmethod
    def _load_request(path: Path) -> ChangeRequest:
        with path.open("r", encoding="utf-8") as stream:
            return ChangeRequest.model_validate(json.load(stream))

    @staticmethod
    def _ratio(numerator: int, denominator: int) -> float:
        return numerator / denominator if denominator else 0.0

    def _metrics(
        self,
        suite: EvaluationSuite,
        results: tuple[EvaluationCaseResult, ...],
    ) -> EvaluationMetrics:
        total = len(results)
        expected_escalations = [
            result
            for case, result in zip(suite.cases, results, strict=True)
            if case.expected_status is DecisionStatus.ESCALATE
        ]
        expected_non_allow = [
            result
            for case, result in zip(suite.cases, results, strict=True)
            if case.expected_status not in ALLOW_STATUSES
        ]
        expected_allow = [
            result
            for case, result in zip(suite.cases, results, strict=True)
            if case.expected_status in ALLOW_STATUSES
        ]
        expected_no_human = [
            result
            for case, result in zip(suite.cases, results, strict=True)
            if not case.human_decision_expected
        ]
        hallucinated_count = sum(len(result.hallucinated_policy_ids) for result in results)
        applied_policy_slots = sum(max(1, len(case.required_policy_ids)) for case in suite.cases)
        return EvaluationMetrics(
            total_cases=total,
            passed_cases=sum(result.passed for result in results),
            decision_accuracy=self._ratio(sum(result.status_correct for result in results), total),
            tool_selection_accuracy=self._ratio(
                sum(result.tool_selection_correct for result in results), total
            ),
            escalation_accuracy=self._ratio(
                sum(
                    result.observed_status is DecisionStatus.ESCALATE
                    for result in expected_escalations
                ),
                len(expected_escalations),
            ),
            policy_grounding_rate=self._ratio(
                sum(result.policy_grounded for result in results), total
            ),
            evidence_completeness_rate=self._ratio(
                sum(result.evidence_complete for result in results), total
            ),
            false_allow_rate=self._ratio(
                sum(result.observed_status in ALLOW_STATUSES for result in expected_non_allow),
                len(expected_non_allow),
            ),
            false_deny_rate=self._ratio(
                sum(result.observed_status in DENY_STATUSES for result in expected_allow),
                len(expected_allow),
            ),
            hallucinated_policy_rate=self._ratio(hallucinated_count, applied_policy_slots),
            unnecessary_human_interruption_rate=self._ratio(
                sum(
                    result.observed_status is DecisionStatus.ESCALATE
                    for result in expected_no_human
                ),
                len(expected_no_human),
            ),
        )
