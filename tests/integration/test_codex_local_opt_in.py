from __future__ import annotations

import os
import unittest
from pathlib import Path

from governor_agent.intelligence import run_codex_spike


@unittest.skipUnless(
    os.environ.get("GOVERNOR_RUN_CODEX_INTEGRATION") == "1",
    "local authenticated Codex integration is opt-in",
)
class CodexLocalIntegrationTest(unittest.TestCase):
    def test_synthetic_read_only_spike_returns_structured_risks(self) -> None:
        raw_home = os.environ.get("GOVERNOR_CODEX_HOME")
        self.assertIsNotNone(raw_home, "set GOVERNOR_CODEX_HOME to an explicit absolute path")

        result = run_codex_spike(Path(raw_home))

        self.assertEqual(result.authority, "ADVISORY_ONLY")
        self.assertEqual(result.provider, "codex-exec")
        self.assertTrue(result.report.risks)
