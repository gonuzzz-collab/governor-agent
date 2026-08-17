"""Structured outputs and run results for the Strands layer."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field

from governor_agent.domain import DecisionStatus
from governor_agent.workflow import WorkflowResult


class AgentGovernanceReport(BaseModel):
    """Model-authored summary that must match the deterministic decision."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    request_id: str = Field(min_length=1)
    decision_id: str = Field(pattern=r"^gov-[0-9a-f]{16}$")
    status: DecisionStatus
    explanation: str = Field(min_length=1)
    human_decision_required: bool
    tools_used: tuple[str, ...] = Field(min_length=3)


@dataclass(frozen=True)
class AgentRunResult:
    """Verified Strands result plus the authoritative workflow result."""

    report: AgentGovernanceReport
    workflow: WorkflowResult
    tool_trace: tuple[str, ...]
