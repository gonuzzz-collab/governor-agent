from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from governor_agent.adapters import GovernanceSourceError, SyntheticFactoryAdapter
from governor_agent.audit import AuditStore
from governor_agent.domain import ChangeRequest
from governor_agent.workflow import GovernorWorkflow


ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "fixtures" / "demo_factory"


class GovernanceBundleContractTest(unittest.TestCase):
    """Every normative registry must load before Governor can make a decision."""

    def test_valid_bundle_evaluates_the_safe_scenario(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            factory = Path(directory) / "factory"
            shutil.copytree(FACTORY, factory)
            workflow = GovernorWorkflow(
                SyntheticFactoryAdapter(factory), AuditStore(Path(directory) / "audit")
            )
            result = workflow.evaluate(self._safe_request(factory))
        self.assertEqual(result.decision.status.value, "ALLOW")

    def test_each_corrupt_normative_registry_blocks_the_workflow(self) -> None:
        corruptions = {
            "authorities.json": {"authorities": []},
            "capabilities.json": {"capabilities": []},
            "policies.json": {"policies": []},
            "permits.json": [],
            "validators.json": [],
        }
        for filename, payload in corruptions.items():
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as directory:
                factory = Path(directory) / "factory"
                shutil.copytree(FACTORY, factory)
                (factory / filename).write_text(json.dumps(payload), encoding="utf-8")
                workflow = GovernorWorkflow(
                    SyntheticFactoryAdapter(factory), AuditStore(Path(directory) / "audit")
                )
                with self.assertRaisesRegex(GovernanceSourceError, f"invalid {filename}"):
                    workflow.evaluate(self._safe_request(factory))

    @staticmethod
    def _safe_request(factory: Path) -> ChangeRequest:
        with (factory / "scenarios" / "safe.json").open(encoding="utf-8") as stream:
            return ChangeRequest.model_validate(json.load(stream))
