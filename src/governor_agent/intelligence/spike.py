"""Synthetic, opt-in proof that Governor can use authenticated local Codex."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from governor_agent.domain import EvidenceKind
from governor_agent.evidence import (
    EvidenceProvenance,
    EvidenceStatement,
    ExternalProcessingAction,
    FactValueKind,
    InformationClassification,
    SanitizedEvidence,
    SourceRole,
    TrustLevel,
)
from governor_agent.intelligence.codex_exec import CodexExecConfig, CodexExecIntelligenceProvider
from governor_agent.intelligence.models import IntelligenceEnvelope, IntelligenceRequest
from governor_agent.intelligence.runner import GovernorIntelligenceRunner

SPIKE_EVIDENCE = SanitizedEvidence(
    evidence_id="ev-synthetic-boundary",
    classification=InformationClassification.PUBLIC,
    project_alias="PUBLIC_GOVERNOR_SPIKE",
    component_alias="PUBLIC_INTELLIGENCE_BOUNDARY",
    event_type="architecture_observation",
    statements=(
        EvidenceStatement(
            statement_id="statement_1",
            kind=EvidenceKind.FACT,
            name="decision_authority",
            value="Deterministic Governor code owns ALLOW, DENY, and ESCALATE.",
            value_kind=FactValueKind.FREE_TEXT,
            trust_level=TrustLevel.TRUSTED_GOVERNANCE,
        ),
        EvidenceStatement(
            statement_id="statement_2",
            kind=EvidenceKind.FACT,
            name="context_boundary",
            value="Codex receives bounded structured evidence through a purpose-built Strands tool.",
            value_kind=FactValueKind.FREE_TEXT,
            trust_level=TrustLevel.TRUSTED_GOVERNANCE,
        ),
        EvidenceStatement(
            statement_id="statement_3",
            kind=EvidenceKind.FACT,
            name="execution_boundary",
            value="The Codex process is read-only and cannot request approval.",
            value_kind=FactValueKind.FREE_TEXT,
            trust_level=TrustLevel.TRUSTED_GOVERNANCE,
        ),
        EvidenceStatement(
            statement_id="statement_4",
            kind=EvidenceKind.FACT,
            name="contest_provider",
            value="Bedrock remains optional for the public contest runtime.",
            value_kind=FactValueKind.FREE_TEXT,
            trust_level=TrustLevel.TRUSTED_GOVERNANCE,
        ),
    ),
    provenance=EvidenceProvenance(
        source_type="synthetic_fixture",
        source_role=SourceRole.NORMATIVE,
        trust_level=TrustLevel.TRUSTED_GOVERNANCE,
        logical_source="factory://synthetic/codex-spike",
    ),
    external_processing_allowed=True,
    external_processing_action=ExternalProcessingAction.ALLOW,
    timestamp=datetime(2026, 8, 17, tzinfo=timezone.utc),
)

SPIKE_REQUEST = IntelligenceRequest(
    objective="Identify architectural risks in a local Codex intelligence boundary.",
    scope=(
        "Synthetic evidence only",
        "Read-only advisory analysis",
        "No governance decision or repository mutation",
    ),
    evidence=(SPIKE_EVIDENCE,),
)


def run_codex_spike(
    codex_home: Path,
    *,
    executable: str = "codex",
    timeout_seconds: int = 120,
) -> IntelligenceEnvelope:
    """Run the fixed synthetic spike; callers must provide explicit runtime consent."""

    provider = CodexExecIntelligenceProvider(
        CodexExecConfig(
            codex_home=codex_home,
            executable=executable,
            timeout_seconds=timeout_seconds,
        )
    )
    return GovernorIntelligenceRunner(provider, SPIKE_REQUEST).run()
