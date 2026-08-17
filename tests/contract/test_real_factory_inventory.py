from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from governor_agent.adapters import (
    GoNucleoFactoryInventoryAdapter,
    GovernanceSourceError,
    SourceReadiness,
)


class RealFactoryInventoryContractTest(unittest.TestCase):
    def create_factory(self, root: Path) -> None:
        (root / ".skills").mkdir()
        (root / ".gonucleo-factory.toml").write_text(
            'schema = "factory.v1"\nid = "test-factory"\n', encoding="utf-8"
        )
        (root / ".skills" / "factory-catalog.toml").write_text(
            """schema_version = 2

[[projects]]
id = "sample"
path = "apps/sample"
adoption = "golden-path"
portfolio = "reference"
""",
            encoding="utf-8",
        )
        (root / ".skills" / "project-golden-path").write_text("tool", encoding="utf-8")
        (root / ".skills" / "change-permit").write_text("tool", encoding="utf-8")

    def test_inventory_is_aggregate_and_fails_readiness_honestly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "factory"
            root.mkdir()
            self.create_factory(root)
            report = GoNucleoFactoryInventoryAdapter(root).inspect()
        self.assertEqual(report.factory_id, "test-factory")
        self.assertEqual(report.project_count, 1)
        self.assertEqual(report.adoption_counts, {"golden-path": 1})
        self.assertFalse(report.ready_for_governance_evaluation)
        statuses = {item.source: item.readiness for item in report.sources}
        self.assertEqual(statuses["project_catalog"], SourceReadiness.AVAILABLE)
        self.assertEqual(statuses["golden_path_tool"], SourceReadiness.PARTIAL)
        self.assertEqual(statuses["capability_registry"], SourceReadiness.MISSING)
        capability = next(item for item in report.sources if item.source == "capability_registry")
        self.assertIsNone(capability.relative_location)
        serialized = report.model_dump_json()
        self.assertNotIn("apps/sample", serialized)
        self.assertNotIn('"sample"', serialized)

    def test_catalog_path_escape_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "factory"
            root.mkdir()
            self.create_factory(root)
            catalog = root / ".skills" / "factory-catalog.toml"
            catalog.write_text(
                """schema_version = 2
[[projects]]
id = "escape"
path = "../outside"
adoption = "legacy"
portfolio = "legacy-review"
""",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(GovernanceSourceError, "unsafe path"):
                GoNucleoFactoryInventoryAdapter(root).inspect()

    def test_factory_root_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "factory"
            root.mkdir()
            self.create_factory(root)
            link = Path(directory) / "linked"
            link.symlink_to(root, target_is_directory=True)
            with self.assertRaisesRegex(GovernanceSourceError, "must not be a symlink"):
                GoNucleoFactoryInventoryAdapter(link)
