from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from governor_agent.adapters import ValidatorKind, ValidatorSpec
from governor_agent.adapters import SyntheticFactoryAdapter
from governor_agent.audit import AuditIntegrityError, AuditStore
from governor_agent.domain import ChangeRequest, ValidationStatus
from governor_agent.validation import ApprovedValidatorRunner
from governor_agent.workflow import GovernorWorkflow


ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "fixtures" / "demo_factory"


class PathConfinementTest(unittest.TestCase):
    def test_requested_file_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            root.mkdir()
            outside = Path(directory) / "outside.py"
            outside.write_text("secret = True\n", encoding="utf-8")
            (root / "escape.py").symlink_to(outside)
            request = ChangeRequest(
                id="req-symlink",
                project="demo",
                objective="Inspect a symlink",
                actor="builder",
                capability="edit",
                requested_scope=("**",),
                files=("escape.py",),
            )
            result = ApprovedValidatorRunner(root).run(
                ValidatorSpec(id="files", kind=ValidatorKind.FILES_EXIST), request
            )
            self.assertEqual(result.status, ValidationStatus.FAIL)
            self.assertIn("symlink", result.summary)

    def test_tampered_audit_record_is_rejected(self) -> None:
        import json

        with tempfile.TemporaryDirectory() as directory:
            audit = AuditStore(Path(directory) / "audit")
            with (FACTORY / "scenarios" / "safe.json").open(encoding="utf-8") as stream:
                request = ChangeRequest.model_validate(json.load(stream))
            result = GovernorWorkflow(SyntheticFactoryAdapter(FACTORY), audit).evaluate(request)
            with result.audit_path.open(encoding="utf-8") as stream:
                payload = json.load(stream)
            payload["decision"]["explanation"] = "Tampered after the decision."
            with result.audit_path.open("w", encoding="utf-8") as stream:
                json.dump(payload, stream)
            with self.assertRaisesRegex(AuditIntegrityError, "digest mismatch"):
                audit.verify(result.audit_path)

    def test_audit_record_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            audit_root = Path(directory) / "audit"
            runs = audit_root / "runs"
            runs.mkdir(parents=True)
            outside = Path(directory) / "outside.json"
            outside.write_text("{}", encoding="utf-8")
            link = runs / "linked.json"
            link.symlink_to(outside)
            with self.assertRaisesRegex(AuditIntegrityError, "must not be a symlink"):
                AuditStore(audit_root).verify(link)
