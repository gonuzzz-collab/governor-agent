"""Deterministic governance evaluation.

The evaluator never asks a model whether a hard rule should be enforced.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from governor_agent.domain.models import (
    DecisionStatus,
    EvaluationContext,
    EvidenceItem,
    EvidenceKind,
    EvidenceStatus,
    GovernanceDecision,
    HumanDecisionRequest,
    Lifecycle,
    PermitStatus,
    PolicyKind,
    ValidationStatus,
    Violation,
)
from governor_agent.domain.paths import matches_patterns


class GovernanceEvaluator:
    """Evaluate a fully resolved governance context with fail-closed rules."""

    def evaluate(
        self,
        context: EvaluationContext,
        *,
        now: datetime | None = None,
    ) -> GovernanceDecision:
        evaluation_time = now or datetime.now(timezone.utc)
        if evaluation_time.tzinfo is None:
            raise ValueError("evaluation time must include a timezone")

        request = context.request
        capability = context.capability
        permit = context.permit
        policy_ids = tuple(sorted(policy.id for policy in context.policies))
        prohibited_scope = tuple(
            sorted(
                {
                    path
                    for policy in context.policies
                    if policy.kind is PolicyKind.FORBIDDEN_PATH
                    for path in policy.paths
                }
            )
        )
        evidence = self._evidence(context, evaluation_time)
        required_validators = self._required_validators(context)

        if capability.lifecycle in {Lifecycle.DEPRECATED, Lifecycle.RETIRED}:
            return self._decision(
                context,
                DecisionStatus.DENY,
                evidence,
                (
                    Violation(
                        code="capability_not_eligible",
                        message=f"Capability lifecycle is {capability.lifecycle.value}.",
                    ),
                ),
                (),
                policy_ids,
                prohibited_scope,
                required_validators,
                "The requested capability is not eligible for new work.",
                evaluation_time,
            )

        if request.action not in capability.allowed_actions:
            return self._decision(
                context,
                DecisionStatus.DENY,
                evidence,
                (
                    Violation(
                        code="capability_action_forbidden",
                        message="The capability contract does not allow the requested action.",
                    ),
                ),
                (),
                policy_ids,
                prohibited_scope,
                required_validators,
                "The capability contract forbids this action.",
                evaluation_time,
            )

        authority_problem = self._authority_problem(context, evaluation_time)
        if authority_problem is not None:
            human_request = HumanDecisionRequest(
                question="Grant an authority scope that explicitly covers this request?",
                context=authority_problem.message,
                options=("grant a narrower authority", "reject the requested change"),
                risks=("Granting authority may expand the actor's permitted effects.",),
            )
            return self._decision(
                context,
                DecisionStatus.ESCALATE,
                evidence,
                (authority_problem,),
                (human_request,),
                policy_ids,
                prohibited_scope,
                required_validators,
                "The actor lacks explicit authority. Governor cannot grant it.",
                evaluation_time,
            )

        permit_problem = self._permit_problem(context, evaluation_time)
        if permit_problem is not None:
            return self._decision(
                context,
                DecisionStatus.DENY,
                evidence,
                (permit_problem,),
                (),
                policy_ids,
                prohibited_scope,
                required_validators,
                "The change permit does not authorize this request.",
                evaluation_time,
            )

        scope_problem = self._scope_problem(context)
        if scope_problem is not None:
            return self._decision(
                context,
                DecisionStatus.DENY,
                evidence,
                (scope_problem,),
                (),
                policy_ids,
                prohibited_scope,
                required_validators,
                "A requested file is outside an explicit allowed scope.",
                evaluation_time,
            )

        policy_problem = self._forbidden_path_problem(context)
        if policy_problem is not None:
            return self._decision(
                context,
                DecisionStatus.DENY,
                evidence,
                (policy_problem,),
                (),
                policy_ids,
                prohibited_scope,
                required_validators,
                "A deterministic policy forbids the requested path.",
                evaluation_time,
            )

        validation_map = {result.validator_id: result for result in context.validations}
        missing_validators = tuple(
            validator_id
            for validator_id in required_validators
            if validator_id not in validation_map
        )
        if missing_validators:
            return self._decision(
                context,
                DecisionStatus.INCOMPLETE_EVIDENCE,
                evidence,
                tuple(
                    Violation(
                        code="missing_validator",
                        message=f"Required validator did not run: {validator_id}",
                    )
                    for validator_id in missing_validators
                ),
                (),
                policy_ids,
                prohibited_scope,
                required_validators,
                "Mandatory validation evidence is incomplete.",
                evaluation_time,
            )

        failed_validations = tuple(
            result
            for result in context.validations
            if result.validator_id in required_validators
            and result.status in {ValidationStatus.FAIL, ValidationStatus.ERROR}
        )
        if failed_validations:
            return self._decision(
                context,
                DecisionStatus.VALIDATION_FAILED,
                evidence,
                tuple(
                    Violation(
                        code="validator_failed",
                        message=f"{result.validator_id}: {result.summary}",
                    )
                    for result in failed_validations
                ),
                (),
                policy_ids,
                prohibited_scope,
                required_validators,
                "At least one approved validator failed.",
                evaluation_time,
            )

        required_evidence = (
            set(request.expected_evidence)
            | set(capability.evidence_required)
            | (set(permit.evidence_required) if permit is not None else set())
        )
        observed_evidence = {
            evidence_type
            for item in context.evidence
            if item.status is EvidenceStatus.OK
            for evidence_type in item.evidence_types
        }
        observed_evidence.update(
            evidence_type
            for result in context.validations
            if result.status is ValidationStatus.PASS
            for evidence_type in result.evidence_types
        )
        missing_evidence = tuple(sorted(required_evidence - observed_evidence))
        if missing_evidence:
            return self._decision(
                context,
                DecisionStatus.INCOMPLETE_EVIDENCE,
                evidence,
                tuple(
                    Violation(
                        code="missing_evidence",
                        message=f"Required evidence is missing: {evidence_type}",
                    )
                    for evidence_type in missing_evidence
                ),
                (),
                policy_ids,
                prohibited_scope,
                required_validators,
                "Required evidence types are incomplete.",
                evaluation_time,
            )

        ownership_request = self._ownership_decision(context)
        if ownership_request is not None:
            return self._decision(
                context,
                DecisionStatus.ESCALATE,
                evidence,
                (),
                (ownership_request,),
                policy_ids,
                prohibited_scope,
                required_validators,
                "Technical validation passed, but persistence ownership requires human authority.",
                evaluation_time,
            )

        status = (
            DecisionStatus.ALLOW_WITH_CONDITIONS
            if capability.lifecycle is Lifecycle.EXPERIMENTAL
            else DecisionStatus.ALLOW
        )
        explanation = (
            "All deterministic governance gates passed. Experimental capability use remains "
            "conditioned on this named request."
            if status is DecisionStatus.ALLOW_WITH_CONDITIONS
            else "All deterministic governance gates and required validations passed."
        )
        return self._decision(
            context,
            status,
            evidence,
            (),
            (),
            policy_ids,
            prohibited_scope,
            required_validators,
            explanation,
            evaluation_time,
        )

    @staticmethod
    def _authority_problem(
        context: EvaluationContext,
        now: datetime,
    ) -> Violation | None:
        request = context.request
        authority = context.authority
        if authority.actor != request.actor:
            return Violation(
                code="authority_actor_mismatch",
                message="The authority grant belongs to a different actor.",
            )
        if authority.expires_at is not None and authority.expires_at <= now:
            return Violation(code="authority_expired", message="The authority grant has expired.")
        if request.action not in authority.allowed_actions:
            return Violation(
                code="authority_action_missing",
                message="The authority grant does not include the requested action.",
            )
        if request.environment not in authority.environments:
            return Violation(
                code="authority_environment_mismatch",
                message="The authority grant does not include the requested environment.",
            )
        for path in request.files:
            if not matches_patterns(path, authority.allowed_paths):
                return Violation(
                    code="authority_scope_missing",
                    message="The authority grant does not include a requested path.",
                    path=path,
                )
        return None

    @staticmethod
    def _permit_problem(
        context: EvaluationContext,
        now: datetime,
    ) -> Violation | None:
        request = context.request
        permit = context.permit
        if permit is None:
            return Violation(code="permit_missing", message="A change permit is required.")
        if permit.status is not PermitStatus.ACTIVE:
            return Violation(
                code="permit_inactive",
                message=f"Permit status is {permit.status.value}.",
            )
        if permit.expires_at is not None and permit.expires_at <= now:
            return Violation(code="permit_expired", message="The change permit has expired.")
        if permit.request_id != request.id:
            return Violation(
                code="permit_request_mismatch", message="Permit request ID does not match."
            )
        if permit.actor != request.actor:
            return Violation(code="permit_actor_mismatch", message="Permit actor does not match.")
        if permit.capability != request.capability:
            return Violation(
                code="permit_capability_mismatch",
                message="Permit capability does not match.",
            )
        if permit.environment != request.environment:
            return Violation(
                code="permit_environment_mismatch",
                message="Permit environment does not match.",
            )
        if request.action in permit.forbidden_actions:
            return Violation(
                code="permit_action_forbidden",
                message="The requested action is explicitly forbidden by the permit.",
            )
        if request.action not in permit.allowed_actions:
            return Violation(
                code="permit_action_missing",
                message="The requested action is not allowed by the permit.",
            )
        return None

    @staticmethod
    def _scope_problem(context: EvaluationContext) -> Violation | None:
        request = context.request
        permit = context.permit
        assert permit is not None
        for path in request.files:
            if not matches_patterns(path, request.requested_scope):
                return Violation(
                    code="request_scope_violation",
                    message="A file is outside the request's declared scope.",
                    path=path,
                )
            if not matches_patterns(path, permit.allowed_paths):
                return Violation(
                    code="permit_scope_violation",
                    message="A file is outside the permit's allowed paths.",
                    path=path,
                )
        return None

    @staticmethod
    def _forbidden_path_problem(context: EvaluationContext) -> Violation | None:
        for policy in context.policies:
            if policy.kind is not PolicyKind.FORBIDDEN_PATH:
                continue
            for path in context.request.files:
                if matches_patterns(path, policy.paths):
                    return Violation(
                        code="policy_forbidden_path",
                        message=policy.description,
                        policy_id=policy.id,
                        path=path,
                    )
        return None

    @staticmethod
    def _required_validators(context: EvaluationContext) -> tuple[str, ...]:
        validators = set(context.capability.validators)
        if context.permit is not None:
            validators.update(context.permit.validators)
        validators.update(
            policy.required_validator
            for policy in context.policies
            if policy.kind is PolicyKind.REQUIRED_VALIDATOR
            and policy.required_validator is not None
        )
        return tuple(sorted(validators))

    @staticmethod
    def _ownership_decision(context: EvaluationContext) -> HumanDecisionRequest | None:
        request = context.request
        for policy in context.policies:
            if policy.kind is not PolicyKind.PERSISTENCE_OWNERSHIP:
                continue
            assert policy.trigger_effect is not None
            assert policy.existing_source is not None
            if policy.trigger_effect not in request.effects:
                continue
            return HumanDecisionRequest(
                question="Which persistence source should be authoritative?",
                context=(
                    f"Existing source of truth: {policy.existing_source}. "
                    "The proposed change introduces another authoritative persistence path."
                ),
                options=policy.options,
                risks=(
                    "Two unsynchronized sources can diverge.",
                    "Changing ownership without a migration plan can lose or orphan data.",
                ),
            )
        return None

    @staticmethod
    def _evidence(
        context: EvaluationContext,
        now: datetime,
    ) -> tuple[EvidenceItem, ...]:
        items = list(context.evidence)
        items.append(
            EvidenceItem(
                evidence_id=f"capability:{context.capability.id}@{context.capability.version}",
                kind=EvidenceKind.FACT,
                source="governance_source",
                subject=context.capability.id,
                status=EvidenceStatus.OK,
                detail=(
                    f"Capability lifecycle is {context.capability.lifecycle.value}; "
                    f"version {context.capability.version}."
                ),
                timestamp=now,
            )
        )
        items.extend(
            EvidenceItem(
                evidence_id=f"policy:{policy.id}",
                kind=EvidenceKind.POLICY,
                source="governance_source",
                subject=policy.id,
                status=EvidenceStatus.OK,
                detail=policy.description,
                timestamp=now,
            )
            for policy in context.policies
        )
        items.extend(
            EvidenceItem(
                evidence_id=f"validator:{result.validator_id}",
                kind=EvidenceKind.FACT,
                source=result.validator_id,
                subject=context.request.id,
                status=(
                    EvidenceStatus.OK
                    if result.status is ValidationStatus.PASS
                    else EvidenceStatus.FAIL
                ),
                detail=result.summary,
                evidence_types=result.evidence_types,
                timestamp=now,
            )
            for result in context.validations
        )
        return tuple(items)

    @staticmethod
    def _decision(
        context: EvaluationContext,
        status: DecisionStatus,
        evidence: tuple[EvidenceItem, ...],
        violations: tuple[Violation, ...],
        human_decisions: tuple[HumanDecisionRequest, ...],
        policy_ids: tuple[str, ...],
        prohibited_scope: tuple[str, ...],
        required_validators: tuple[str, ...],
        explanation: str,
        timestamp: datetime,
    ) -> GovernanceDecision:
        request = context.request
        permit = context.permit
        identity_payload = {
            "request_id": request.id,
            "status": status.value,
            "violations": [violation.code for violation in violations],
            "policies": list(policy_ids),
            "human_questions": [item.question for item in human_decisions],
        }
        digest = hashlib.sha256(
            json.dumps(identity_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()[:16]
        return GovernanceDecision(
            decision_id=f"gov-{digest}",
            project=request.project,
            request_id=request.id,
            status=status,
            risk_level=request.risk_level,
            authority_required=request.action,
            authority_available=tuple(sorted(context.authority.allowed_actions)),
            policies_applied=policy_ids,
            capabilities_required=(f"{context.capability.id}@{context.capability.version}",),
            evidence=evidence,
            violations=violations,
            allowed_scope=permit.allowed_paths if permit is not None else (),
            prohibited_scope=prohibited_scope,
            validations_required=required_validators,
            automatic_actions=("inspect", "evaluate", "record_decision"),
            human_decisions=human_decisions,
            explanation=explanation,
            timestamp=timestamp,
        )
