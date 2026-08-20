from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from governor_agent.cli import main
from governor_agent.intelligence import IntelligenceEnvelope


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

    def test_codex_requires_explicit_quota_acknowledgement(self) -> None:
        with io.StringIO() as error, contextlib.redirect_stderr(error):
            code = main(
                [
                    "codex-spike",
                    "--codex-home",
                    "/explicit/codex-home",
                ]
            )
            error_text = error.getvalue()
        self.assertEqual(code, 2)
        self.assertIn("--allow-codex", error_text)

    @patch("governor_agent.cli.run_codex_spike")
    def test_codex_spike_renders_advisory_json(self, fake_spike) -> None:
        fake_spike.return_value = IntelligenceEnvelope(
            report={
                "summary": "Synthetic result.",
                "risks": [
                    {
                        "risk": "Context could be broader than required.",
                        "evidence": ["Context is explicitly bounded."],
                    }
                ],
            }
        )
        with io.StringIO() as output, contextlib.redirect_stdout(output):
            code = main(
                [
                    "codex-spike",
                    "--codex-home",
                    "/explicit/codex-home",
                    "--allow-codex",
                    "--format",
                    "json",
                ]
            )
            output_text = output.getvalue()
        payload = json.loads(output_text)
        self.assertEqual(code, 0)
        self.assertEqual(payload["authority"], "ADVISORY_ONLY")
        self.assertNotIn("status", payload["report"])
        fake_spike.assert_called_once_with(Path("/explicit/codex-home"))

    def test_agent_evaluation_cli_reports_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as directory, io.StringIO() as output:
            with contextlib.redirect_stdout(output):
                code = main(
                    [
                        "eval-agent",
                        "--factory",
                        str(FACTORY),
                        "--suite",
                        str(ROOT / "evals" / "core_suite.json"),
                        "--audit-dir",
                        directory,
                    ]
                )
            text = output.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("Cases passed: 9/9", text)
        self.assertIn("False allow rate: 0.000", text)

    def test_verify_audit_cli_confirms_digest(self) -> None:
        with tempfile.TemporaryDirectory() as directory, io.StringIO() as output:
            audit_dir = Path(directory) / "audit"
            with contextlib.redirect_stdout(output):
                self.assertEqual(
                    main(
                        [
                            "demo",
                            "safe",
                            "--factory",
                            str(FACTORY),
                            "--audit-dir",
                            str(audit_dir),
                        ]
                    ),
                    0,
                )
                record = next((audit_dir / "runs").glob("*.json"))
                code = main(
                    [
                        "verify-audit",
                        str(record),
                        "--audit-dir",
                        str(audit_dir),
                    ]
                )
            text = output.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("Audit integrity: VERIFIED", text)

    def test_debug_mode_exposes_ids_without_raw_validator_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory, io.StringIO() as output:
            with contextlib.redirect_stdout(output):
                code = main(
                    [
                        "--debug",
                        "agent-demo",
                        "safe",
                        "--factory",
                        str(FACTORY),
                        "--audit-dir",
                        directory,
                    ]
                )
            text = output.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("Decision ID: gov-", text)
        self.assertIn("Evidence IDs:", text)
        self.assertNotIn("test_normalize_key", text)

    def test_real_factory_inspection_is_aggregate_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory, io.StringIO() as output:
            root = Path(directory) / "factory"
            (root / ".skills").mkdir(parents=True)
            (root / ".gonucleo-factory.toml").write_text(
                'schema = "factory.v1"\nid = "private-factory"\n', encoding="utf-8"
            )
            (root / ".skills" / "factory-catalog.toml").write_text(
                """schema_version = 2
[[projects]]
id = "private-project-name"
path = "apps/private-project-name"
adoption = "legacy"
portfolio = "legacy-review"
""",
                encoding="utf-8",
            )
            with contextlib.redirect_stdout(output):
                code = main(["inspect-factory", str(root), "--format", "json"])
            output_text = output.getvalue()
            payload = json.loads(output_text)
        self.assertEqual(code, 0)
        self.assertEqual(payload["project_count"], 1)
        self.assertNotIn("private-project-name", output_text)

    def test_real_factory_evidence_cli_is_sanitized_and_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory, io.StringIO() as output:
            root = Path(directory) / "factory"
            (root / ".skills").mkdir(parents=True)
            (root / ".gonucleo-factory.toml").write_text(
                'schema = "factory.v1"\nid = "private-factory"\n', encoding="utf-8"
            )
            (root / ".skills" / "factory-catalog.toml").write_text(
                """schema_version = 2
[[projects]]
id = "private-project-name"
path = "apps/private-project-name"
adoption = "legacy"
portfolio = "legacy-review"
""",
                encoding="utf-8",
            )
            audit_root = Path(directory) / "audit"
            with contextlib.redirect_stdout(output):
                code = main(
                    [
                        "inspect-factory-evidence",
                        str(root),
                        "--audit-dir",
                        str(audit_root),
                        "--format",
                        "json",
                    ]
                )
            output_text = output.getvalue()
            payload = json.loads(output_text)

        self.assertEqual(code, 5)
        self.assertEqual(payload["governance_status"], "INCOMPLETE_EVIDENCE")
        self.assertFalse(payload["authoritative_change_decision"])
        self.assertNotIn("private-factory", output_text)
        self.assertNotIn("private-project-name", output_text)
        self.assertNotIn(str(root), output_text)

    def test_real_factory_codex_requires_home_and_quota_acknowledgement_together(self) -> None:
        with io.StringIO() as error, contextlib.redirect_stderr(error):
            code = main(
                [
                    "inspect-factory-evidence",
                    "/not-read-because-gate-runs-first",
                    "--allow-codex",
                ]
            )
            error_text = error.getvalue()
        self.assertEqual(code, 2)
        self.assertIn("both --allow-codex and --codex-home", error_text)
