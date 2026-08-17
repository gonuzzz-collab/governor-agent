from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from governor_agent.adapters import SyntheticFactoryAdapter
from governor_agent.audit import AuditStore
from governor_agent.domain import ChangeRequest, DecisionStatus, ValidationStatus
from governor_agent.workflow import GovernorWorkflow


ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "fixtures" / "demo_factory"


def load_request(name: str) -> ChangeRequest:
    with (FACTORY / "scenarios" / f"{name}.json").open(encoding="utf-8") as stream:
        return ChangeRequest.model_validate(json.load(stream))


class SyntheticWorkflowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        source = SyntheticFactoryAdapter(FACTORY)
        self.workflow = GovernorWorkflow(source, AuditStore(Path(self.temporary.name)))

    def test_safe_change_closes_automatically(self) -> None:
        result = self.workflow.evaluate(load_request("safe"))
        self.assertEqual(result.decision.status, DecisionStatus.ALLOW)
        self.assertEqual({item.status for item in result.validations}, {ValidationStatus.PASS})
        self.assertIn("run_approved_validators", result.decision.automatic_actions)
        self.assertIn("close", result.decision.automatic_actions)
        self.assertTrue(result.audit_path.is_file())
        verified = AuditStore(Path(self.temporary.name)).verify(result.audit_path)
        self.assertEqual(verified.run_id, result.audit_record.run_id)

    def test_scope_violation_is_denied_without_running_validators(self) -> None:
        result = self.workflow.evaluate(load_request("deny"))
        self.assertEqual(result.decision.status, DecisionStatus.DENY)
        self.assertEqual(result.validations, ())
        self.assertEqual(result.decision.violations[0].code, "permit_scope_violation")
        self.assertIn("reject", result.decision.automatic_actions)

    def test_ownership_ambiguity_escalates_after_technical_pass(self) -> None:
        result = self.workflow.evaluate(load_request("escalate"))
        self.assertEqual(result.decision.status, DecisionStatus.ESCALATE)
        self.assertEqual({item.status for item in result.validations}, {ValidationStatus.PASS})
        self.assertEqual(len(result.decision.human_decisions), 1)
        self.assertIn("prepare_human_decision", result.decision.automatic_actions)

    def test_repeated_run_appends_instead_of_overwriting(self) -> None:
        first = self.workflow.evaluate(load_request("safe"))
        second = self.workflow.evaluate(load_request("safe"))
        self.assertNotEqual(first.audit_path, second.audit_path)
        self.assertTrue(first.audit_path.is_file())
        self.assertTrue(second.audit_path.is_file())
