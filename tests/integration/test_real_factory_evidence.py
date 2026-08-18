from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from governor_agent.adapters import RealFactoryAdapter
from governor_agent.domain import DecisionStatus
from governor_agent.evidence import EvidenceAuditStore, EvidenceSanitizer, SanitizedEvidence
from governor_agent.intelligence import ArchitecturalRiskReport, IntelligenceRequest
from governor_agent.observation import RealFactoryObservationRunner


class FakeIntelligenceProvider:
    provider_id = "fake"

    def analyze(self, request: IntelligenceRequest) -> ArchitecturalRiskReport:
        self.request = request
        return ArchitecturalRiskReport(
            summary="The factory observation is useful but incomplete.",
            risks=(
                {
                    "risk": "Missing authority contracts prevent a complete governance decision.",
                    "evidence": ["The sanitized readiness evidence reports missing contracts."],
                },
            ),
        )


class RealFactoryEvidenceIntegrationTest(unittest.TestCase):
    def create_factory(self, root: Path) -> None:
        (root / ".skills").mkdir(parents=True)
        (root / ".gonucleo-factory.toml").write_text(
            'schema = "factory.v1"\nid = "private-factory"\n', encoding="utf-8"
        )
        (root / ".skills" / "factory-catalog.toml").write_text(
            """schema_version = 2
[[projects]]
id = "private-project"
path = "apps/private-project"
adoption = "golden-path"
portfolio = "reference"
""",
            encoding="utf-8",
        )

    def test_read_only_observation_is_sanitized_and_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "factory"
            root.mkdir()
            self.create_factory(root)
            audit_root = Path(directory) / "audit"
            source = RealFactoryAdapter(root)
            result = RealFactoryObservationRunner(
                source,
                EvidenceSanitizer(root, private_identifiers=("private-factory",)),
                EvidenceAuditStore(audit_root),
            ).run()
            audit_text = next((audit_root / "evidence-runs").glob("*.json")).read_text(
                encoding="utf-8"
            )

        serialized = result.model_dump_json()
        self.assertEqual(result.governance_status, DecisionStatus.INCOMPLETE_EVIDENCE)
        self.assertFalse(result.authoritative_change_decision)
        self.assertIsNone(result.advisory)
        self.assertIn("authority_registry", result.missing_contracts)
        self.assertIn("validator_registry", result.partial_contracts)
        self.assertNotIn("private-factory", serialized)
        self.assertNotIn("private-project", serialized)
        self.assertNotIn(str(root), serialized)
        self.assertNotIn("private-factory", audit_text)
        self.assertNotIn("private-project", audit_text)

    def test_only_sanitized_evidence_reaches_optional_advisory_provider(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "factory"
            root.mkdir()
            self.create_factory(root)
            provider = FakeIntelligenceProvider()
            audit_root = Path(directory) / "audit"
            result = RealFactoryObservationRunner(
                RealFactoryAdapter(root),
                EvidenceSanitizer(root),
                EvidenceAuditStore(audit_root),
            ).run(intelligence_provider=provider)
            record_path = next((audit_root / "evidence-runs").glob("*.json"))
            record = EvidenceAuditStore(audit_root).verify(record_path)

        self.assertIsNotNone(result.advisory)
        self.assertTrue(
            all(isinstance(item, SanitizedEvidence) for item in provider.request.evidence)
        )
        self.assertTrue(record.codex_received)
        self.assertEqual(record.governor_decision, DecisionStatus.INCOMPLETE_EVIDENCE)

    def test_audit_store_inside_factory_is_rejected_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "factory"
            root.mkdir()
            self.create_factory(root)
            with self.assertRaisesRegex(ValueError, "outside the real factory"):
                RealFactoryObservationRunner(
                    RealFactoryAdapter(root),
                    EvidenceSanitizer(root),
                    EvidenceAuditStore(root / "audit"),
                )
            self.assertFalse((root / "audit").exists())
