from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from governor_agent.domain import EvidenceKind
from governor_agent.evidence import (
    EvidenceBoundaryError,
    EvidenceSanitizer,
    FactValueKind,
    InformationClassification,
    RawEvidence,
    RawFact,
    SourceRole,
    TrustLevel,
)


class EvidenceBoundarySecurityTest(unittest.TestCase):
    def raw(self, source: Path) -> RawEvidence:
        return RawEvidence(
            evidence_id="raw-path-boundary",
            source_type="repository_file",
            classification=InformationClassification.INTERNAL,
            kind=EvidenceKind.FACT,
            trust_level=TrustLevel.UNTRUSTED_REPOSITORY_CONTENT,
            source_role=SourceRole.DESCRIPTIVE,
            local_project="private-project",
            event_type="repository_observation",
            source_path=source,
            facts=(RawFact(name="present", value="true", value_kind=FactValueKind.BOOLEAN),),
        )

    def test_source_outside_factory_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "factory"
            root.mkdir()
            outside = base / "outside.txt"
            outside.write_text("outside", encoding="utf-8")

            with self.assertRaisesRegex(EvidenceBoundaryError, "escapes"):
                EvidenceSanitizer(root).sanitize(self.raw(outside))

    def test_symlink_source_is_rejected_even_when_target_is_inside_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "factory"
            root.mkdir()
            target = root / "target.txt"
            target.write_text("inside", encoding="utf-8")
            link = root / "linked.txt"
            link.symlink_to(target)

            with self.assertRaisesRegex(EvidenceBoundaryError, "symlink"):
                EvidenceSanitizer(root).sanitize(self.raw(link))


if __name__ == "__main__":
    unittest.main()
