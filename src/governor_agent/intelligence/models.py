"""Structured advisory intelligence with no governance-decision fields."""

from __future__ import annotations

from typing import Annotated, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

ShortText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=2_000),
]


class IntelligenceRequest(BaseModel):
    """Minimal context selected by Governor, never by the intelligence provider."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    objective: ShortText
    scope: tuple[ShortText, ...] = Field(min_length=1, max_length=16)
    evidence: tuple[ShortText, ...] = Field(min_length=1, max_length=32)


class ArchitecturalRisk(BaseModel):
    """One advisory risk tied to supplied evidence."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    risk: ShortText
    evidence: tuple[ShortText, ...] = Field(min_length=1, max_length=16)


class ArchitecturalRiskReport(BaseModel):
    """Codex-authored content that cannot encode a governance decision."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    summary: ShortText
    risks: tuple[ArchitecturalRisk, ...] = Field(min_length=1, max_length=16)


class IntelligenceEnvelope(BaseModel):
    """Governor-owned metadata around an untrusted advisory report."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["governor.intelligence.v1"] = "governor.intelligence.v1"
    provider: Literal["codex-exec"] = "codex-exec"
    authority: Literal["ADVISORY_ONLY"] = "ADVISORY_ONLY"
    strands_tool: Literal["analyze_architectural_risks"] = "analyze_architectural_risks"
    report: ArchitecturalRiskReport


class IntelligenceProvider(Protocol):
    """Low-coupling boundary implemented by local or cloud intelligence."""

    @property
    def provider_id(self) -> str: ...

    def analyze(self, request: IntelligenceRequest) -> ArchitecturalRiskReport: ...
