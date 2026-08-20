from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from governor_agent.adapters import GovernanceSourceError, SyntheticFactoryAdapter
from governor_agent.domain import ChangeRequest


ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "fixtures" / "demo_factory"


class SyntheticAdapterContractTest(unittest.TestCase):
    def test_factory_root_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            link = Path(directory) / "factory-link"
            os.symlink(FACTORY, link, target_is_directory=True)
            with self.assertRaisesRegex(GovernanceSourceError, "must not be a symlink"):
                SyntheticFactoryAdapter(link)

    def test_malformed_policy_file_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "factory"
            shutil.copytree(FACTORY, copied)
            with (copied / "policies.json").open("w", encoding="utf-8") as stream:
                json.dump({"not": "a policy list"}, stream)
            source = SyntheticFactoryAdapter(copied)
            with (copied / "scenarios" / "safe.json").open(encoding="utf-8") as stream:
                request = ChangeRequest.model_validate(json.load(stream))
            with self.assertRaisesRegex(GovernanceSourceError, "invalid policies.json"):
                source.get_policies(request)

    def test_duplicate_authority_grants_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "factory"
            shutil.copytree(FACTORY, copied)
            (copied / "authorities.json").write_text(
                json.dumps(
                    {
                        "schema_version": "governor.authority-registry.v1",
                        "authorities": [{"actor": "builder"}, {"actor": "builder"}],
                    }
                ),
                encoding="utf-8",
            )
            source = SyntheticFactoryAdapter(copied)
            with self.assertRaisesRegex(GovernanceSourceError, "invalid authorities.json"):
                source.get_authority("builder")

    def test_legacy_authority_list_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "factory"
            shutil.copytree(FACTORY, copied)
            (copied / "authorities.json").write_text(
                json.dumps([{"actor": "builder"}]), encoding="utf-8"
            )
            source = SyntheticFactoryAdapter(copied)
            with self.assertRaisesRegex(GovernanceSourceError, "invalid authorities.json"):
                source.get_authority("builder")

    def test_missing_authority_schema_version_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "factory"
            shutil.copytree(FACTORY, copied)
            (copied / "authorities.json").write_text(
                json.dumps({"authorities": [{"actor": "builder"}]}), encoding="utf-8"
            )
            source = SyntheticFactoryAdapter(copied)
            with self.assertRaisesRegex(GovernanceSourceError, "invalid authorities.json"):
                source.get_authority("builder")

    def test_legacy_capability_list_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "factory"
            shutil.copytree(FACTORY, copied)
            (copied / "capabilities.json").write_text(
                json.dumps([{"id": "change"}]), encoding="utf-8"
            )
            source = SyntheticFactoryAdapter(copied)
            with self.assertRaisesRegex(GovernanceSourceError, "invalid capabilities.json"):
                source.get_capability("change")

    def test_missing_capability_schema_version_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "factory"
            shutil.copytree(FACTORY, copied)
            (copied / "capabilities.json").write_text(
                json.dumps({"capabilities": []}), encoding="utf-8"
            )
            source = SyntheticFactoryAdapter(copied)
            with self.assertRaisesRegex(GovernanceSourceError, "invalid capabilities.json"):
                source.get_capability("change")

    def test_legacy_permit_list_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "factory"
            shutil.copytree(FACTORY, copied)
            (copied / "permits.json").write_text(
                json.dumps([{"permit_id": "permit", "request_id": "request"}]),
                encoding="utf-8",
            )
            source = SyntheticFactoryAdapter(copied)
            with self.assertRaisesRegex(GovernanceSourceError, "invalid permits.json"):
                source.get_permit("request")

    def test_empty_permit_registry_returns_no_permit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "factory"
            shutil.copytree(FACTORY, copied)
            (copied / "permits.json").write_text(
                json.dumps({"schema_version": "governor.permit-registry.v1", "permits": []}),
                encoding="utf-8",
            )
            source = SyntheticFactoryAdapter(copied)
            self.assertIsNone(source.get_permit("request"))

    def test_legacy_policy_list_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "factory"
            shutil.copytree(FACTORY, copied)
            (copied / "policies.json").write_text(json.dumps([]), encoding="utf-8")
            source = SyntheticFactoryAdapter(copied)
            with (copied / "scenarios" / "safe.json").open(encoding="utf-8") as stream:
                request = ChangeRequest.model_validate(json.load(stream))
            with self.assertRaisesRegex(GovernanceSourceError, "invalid policies.json"):
                source.get_policies(request)
