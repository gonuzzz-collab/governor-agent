"""Synthetic, opt-in proof that Governor can use authenticated local Codex."""

from __future__ import annotations

from pathlib import Path

from governor_agent.intelligence.codex_exec import CodexExecConfig, CodexExecIntelligenceProvider
from governor_agent.intelligence.models import IntelligenceEnvelope, IntelligenceRequest
from governor_agent.intelligence.runner import GovernorIntelligenceRunner

SPIKE_REQUEST = IntelligenceRequest(
    objective="Identify architectural risks in a local Codex intelligence boundary.",
    scope=(
        "Synthetic evidence only",
        "Read-only advisory analysis",
        "No governance decision or repository mutation",
    ),
    evidence=(
        "Governor keeps ALLOW, DENY, and ESCALATE in deterministic code.",
        "Codex receives bounded context through a purpose-built Strands tool.",
        "The Codex child process uses a read-only sandbox and cannot request approval.",
        "Amazon Bedrock remains an optional provider for the public contest runtime.",
    ),
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
