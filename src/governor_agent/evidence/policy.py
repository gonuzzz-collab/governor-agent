"""Deterministic external-intelligence policy; no model participates."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from governor_agent.evidence.models import (
    ExternalProcessingAction,
    InformationClassification,
)


class ExternalProcessingAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    action: ExternalProcessingAction
    allowed: bool
    reason: str


class ExternalIntelligencePolicy:
    """Apply the hard information-classification matrix."""

    def evaluate(
        self,
        classification: InformationClassification,
        *,
        secret_detected: bool = False,
    ) -> ExternalProcessingAssessment:
        if secret_detected or classification is InformationClassification.SECRET:
            return ExternalProcessingAssessment(
                action=ExternalProcessingAction.BLOCK_EXTERNAL_EXPOSURE,
                allowed=False,
                reason="Secret-class evidence cannot be processed externally.",
            )
        if classification is InformationClassification.CONFIDENTIAL:
            return ExternalProcessingAssessment(
                action=ExternalProcessingAction.ALLOW_METADATA_ONLY,
                allowed=True,
                reason="Confidential evidence is limited to sanitized structural metadata.",
            )
        if classification is InformationClassification.INTERNAL:
            return ExternalProcessingAssessment(
                action=ExternalProcessingAction.ALLOW_SANITIZED,
                allowed=True,
                reason="Internal evidence requires minimization and sanitization.",
            )
        return ExternalProcessingAssessment(
            action=ExternalProcessingAction.ALLOW,
            allowed=True,
            reason="Public evidence may be processed externally when necessary.",
        )
