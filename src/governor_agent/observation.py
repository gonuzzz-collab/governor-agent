"""Read-only real-factory evidence observation through the sanitized boundary."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from governor_agent.adapters import FactoryEvidenceSource
from governor_agent.domain import DecisionStatus
from governor_agent.evidence import EvidenceAuditStore, EvidenceSanitizer, SanitizedEvidence
from governor_agent.intelligence import (
    GovernorIntelligenceRunner,
    IntelligenceEnvelope,
    IntelligenceProvider,
    IntelligenceRequest,
)


class FactoryObservationResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["governor.factory-observation.v1"] = "governor.factory-observation.v1"
    governance_status: DecisionStatus
    authoritative_change_decision: Literal[False] = False
    reason: str
    missing_contracts: tuple[str, ...] = ()
    partial_contracts: tuple[str, ...] = ()
    evidence: tuple[SanitizedEvidence, ...] = Field(min_length=1)
    advisory: IntelligenceEnvelope | None = None
    evidence_audit_ids: tuple[str, ...] = Field(min_length=1)


class RealFactoryObservationRunner:
    """Orchestrate fixed-source extraction without exposing the factory to Strands or Codex."""

    def __init__(
        self,
        source: FactoryEvidenceSource,
        sanitizer: EvidenceSanitizer,
        audit_store: EvidenceAuditStore,
    ) -> None:
        try:
            audit_store.root.relative_to(source.factory_root)
        except ValueError:
            pass
        else:
            raise ValueError("evidence audit store must be outside the real factory")
        self._source = source
        self._sanitizer = sanitizer
        self._audit_store = audit_store

    def run(
        self,
        *,
        intelligence_provider: IntelligenceProvider | None = None,
    ) -> FactoryObservationResult:
        collection = self._source.collect_evidence()
        processed = tuple(self._sanitizer.sanitize(item) for item in collection.evidence)
        evidence = tuple(item.evidence for item in processed)
        blocked = any(not item.external_processing_allowed for item in evidence)
        advisory = None
        if intelligence_provider is not None and not blocked:
            request = IntelligenceRequest(
                objective=(
                    "Identify architectural risks and missing governance contracts in this "
                    "read-only factory observation."
                ),
                scope=(
                    "Sanitized aggregate factory evidence only",
                    "No repository access or governance authority",
                ),
                evidence=evidence,
            )
            advisory = GovernorIntelligenceRunner(intelligence_provider, request).run()

        if blocked:
            reason = "External exposure was blocked by deterministic secret policy."
        elif not collection.ready_for_governance_evaluation:
            reason = (
                "Real evidence was sanitized successfully, but mandatory governance contracts "
                "remain unavailable."
            )
        else:
            reason = "Evidence is ready for a separately authorized governance request."
        status = (
            DecisionStatus.INCOMPLETE_EVIDENCE
            if blocked or not collection.ready_for_governance_evaluation
            else DecisionStatus.ESCALATE
        )
        audit_ids = []
        for item in processed:
            record, _ = self._audit_store.record(
                item.audit,
                item.evidence,
                codex_received=advisory is not None,
                governor_decision=status,
            )
            audit_ids.append(record.audit_id)
        return FactoryObservationResult(
            governance_status=status,
            reason=reason,
            missing_contracts=collection.missing_contracts,
            partial_contracts=collection.partial_contracts,
            evidence=evidence,
            advisory=advisory,
            evidence_audit_ids=tuple(audit_ids),
        )
