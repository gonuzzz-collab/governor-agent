from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from governor_agent.cli import main


ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "fixtures" / "demo_factory"


class CliScenarioTest(unittest.TestCase):
    def run_demo(self, scenario: str) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as directory, io.StringIO() as output:
            with contextlib.redirect_stdout(output):
                code = main(
                    [
                        "demo",
                        scenario,
                        "--factory",
                        str(FACTORY),
                        "--audit-dir",
                        directory,
                    ]
                )
            return code, output.getvalue()

    def test_safe_exit_code(self) -> None:
        code, output = self.run_demo("safe")
        self.assertEqual(code, 0)
        self.assertIn("Governor decision: ALLOW", output)

    def test_deny_exit_code(self) -> None:
        code, output = self.run_demo("deny")
        self.assertEqual(code, 4)
        self.assertIn("permit_scope_violation", output)

    def test_escalation_exit_code(self) -> None:
        code, output = self.run_demo("escalate")
        self.assertEqual(code, 3)
        self.assertIn("Human decision required", output)

    def test_all_demo_succeeds_when_contract_matches(self) -> None:
        code, output = self.run_demo("all")
        self.assertEqual(code, 0)
        self.assertIn("=== SAFE ===", output)
        self.assertIn("=== DENY ===", output)
        self.assertIn("=== ESCALATE ===", output)

    def test_all_json_output_is_one_valid_document(self) -> None:
        with tempfile.TemporaryDirectory() as directory, io.StringIO() as output:
            with contextlib.redirect_stdout(output):
                code = main(
                    [
                        "demo",
                        "all",
                        "--factory",
                        str(FACTORY),
                        "--audit-dir",
                        directory,
                        "--format",
                        "json",
                    ]
                )
            payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual([item["scenario"] for item in payload], ["safe", "deny", "escalate"])

    def test_bedrock_requires_explicit_cost_acknowledgement(self) -> None:
        with tempfile.TemporaryDirectory() as directory, io.StringIO() as error:
            with contextlib.redirect_stderr(error):
                code = main(
                    [
                        "agent-demo",
                        "safe",
                        "--factory",
                        str(FACTORY),
                        "--audit-dir",
                        directory,
                        "--model",
                        "bedrock",
                    ]
                )
            error_text = error.getvalue()
        self.assertEqual(code, 2)
        self.assertIn("--allow-paid-inference", error_text)
