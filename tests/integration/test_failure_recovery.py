from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from governor_agent.adapters import SyntheticFactoryAdapter
from governor_agent.audit import AuditStore
from governor_agent.domain import ChangeRequest, DecisionStatus, ValidationStatus
from governor_agent.workflow import GovernorWorkflow


ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "fixtures" / "demo_factory"


class FailureRecoveryTest(unittest.TestCase):
    def copied_factory(self, directory: str) -> Path:
        copied = Path(directory) / "factory"
        shutil.copytree(FACTORY, copied)
        return copied

    def load_safe_request(self, factory: Path) -> ChangeRequest:
        with (factory / "scenarios" / "safe.json").open(encoding="utf-8") as stream:
            return ChangeRequest.model_validate(json.load(stream))

    def test_failed_project_tests_produce_audited_validation_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            factory = self.copied_factory(directory)
            (factory / "project" / "tests" / "test_service.py").write_text(
                "import unittest\n\nclass FailingTest(unittest.TestCase):\n"
                "    def test_failure(self):\n        self.fail('private raw failure')\n",
                encoding="utf-8",
            )
            audit = AuditStore(Path(directory) / "audit")
            result = GovernorWorkflow(SyntheticFactoryAdapter(factory), audit).evaluate(
                self.load_safe_request(factory)
            )
            verified = audit.verify(result.audit_path)

        self.assertEqual(result.decision.status, DecisionStatus.VALIDATION_FAILED)
        self.assertIn("reject", result.decision.automatic_actions)
        self.assertEqual(verified.decision.status, DecisionStatus.VALIDATION_FAILED)
        summaries = " ".join(item.summary for item in result.validations)
        self.assertNotIn("private raw failure", summaries)

    def test_missing_validator_definition_fails_closed_and_is_audited(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            factory = self.copied_factory(directory)
            validators_path = factory / "validators.json"
            with validators_path.open(encoding="utf-8") as stream:
                validators = json.load(stream)
            with validators_path.open("w", encoding="utf-8") as stream:
                json.dump(
                    [item for item in validators if item["id"] != "python-unit-tests"],
                    stream,
                )
            audit = AuditStore(Path(directory) / "audit")
            result = GovernorWorkflow(SyntheticFactoryAdapter(factory), audit).evaluate(
                self.load_safe_request(factory)
            )
            verified = audit.verify(result.audit_path)

        self.assertEqual(result.decision.status, DecisionStatus.VALIDATION_FAILED)
        unavailable = next(
            item for item in result.validations if item.validator_id == "python-unit-tests"
        )
        self.assertEqual(unavailable.status, ValidationStatus.ERROR)
        self.assertEqual(verified.decision.status, DecisionStatus.VALIDATION_FAILED)

    def test_missing_required_evidence_remains_incomplete_after_tests_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            factory = self.copied_factory(directory)
            capability_path = factory / "capabilities.json"
            with capability_path.open(encoding="utf-8") as stream:
                capabilities = json.load(stream)
            capabilities[0]["evidence_required"].append("security-review")
            with capability_path.open("w", encoding="utf-8") as stream:
                json.dump(capabilities, stream)
            audit = AuditStore(Path(directory) / "audit")
            result = GovernorWorkflow(SyntheticFactoryAdapter(factory), audit).evaluate(
                self.load_safe_request(factory)
            )
            verified = audit.verify(result.audit_path)

        self.assertEqual(result.decision.status, DecisionStatus.INCOMPLETE_EVIDENCE)
        self.assertEqual({item.status for item in result.validations}, {ValidationStatus.PASS})
        self.assertIn("missing_evidence", {item.code for item in result.decision.violations})
        self.assertEqual(verified.decision.status, DecisionStatus.INCOMPLETE_EVIDENCE)
