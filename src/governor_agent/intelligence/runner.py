"""Strands tool boundary for advisory intelligence."""

from __future__ import annotations

from typing import Any

from strands import tool

from governor_agent.intelligence.models import (
    ArchitecturalRiskReport,
    IntelligenceEnvelope,
    IntelligenceProvider,
    IntelligenceRequest,
)


class GovernorIntelligenceRunner:
    """Bind one fixed request to a purpose-built Strands tool."""

    def __init__(self, provider: IntelligenceProvider, request: IntelligenceRequest) -> None:
        self._provider = provider
        self._request = request
        self._tool = self._create_tool()

    @property
    def strands_tool(self) -> Any:
        return self._tool

    def run(self) -> IntelligenceEnvelope:
        report = ArchitecturalRiskReport.model_validate(self._tool())
        return IntelligenceEnvelope(report=report)

    def _create_tool(self) -> Any:
        provider = self._provider
        request = self._request

        @tool
        def analyze_architectural_risks() -> dict[str, Any]:
            """Analyze a Governor-fixed evidence package without making a governance decision.

            The human or deterministic Governor caller fixes the request before this tool is exposed.
            The model cannot select paths, widen scope, add evidence, or grant itself authority.
            """

            return provider.analyze(request).model_dump(mode="json")

        return analyze_architectural_risks
