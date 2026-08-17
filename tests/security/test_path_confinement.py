from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from governor_agent.adapters import ValidatorKind, ValidatorSpec
from governor_agent.domain import ChangeRequest, ValidationStatus
from governor_agent.validation import ApprovedValidatorRunner


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
