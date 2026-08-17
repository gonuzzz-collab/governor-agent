from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from governor_agent.evaluation import AgentEvaluationRunner, EvaluationStore


ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "fixtures" / "demo_factory"
SUITE = ROOT / "evals" / "core_suite.json"


class AgentEvaluationRunnerTest(unittest.TestCase):
    def test_core_suite_measures_safe_autonomy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = AgentEvaluationRunner(FACTORY, Path(directory) / "runs").run(SUITE)
            path = EvaluationStore(Path(directory)).record(report)
            self.assertTrue(path.is_file())

        self.assertEqual(report.metrics.total_cases, 4)
        self.assertEqual(report.metrics.passed_cases, 4)
        self.assertEqual(report.metrics.decision_accuracy, 1.0)
        self.assertEqual(report.metrics.tool_selection_accuracy, 1.0)
        self.assertEqual(report.metrics.escalation_accuracy, 1.0)
        self.assertEqual(report.metrics.policy_grounding_rate, 1.0)
        self.assertEqual(report.metrics.evidence_completeness_rate, 1.0)
        self.assertEqual(report.metrics.false_allow_rate, 0.0)
        self.assertEqual(report.metrics.false_deny_rate, 0.0)
        self.assertEqual(report.metrics.hallucinated_policy_rate, 0.0)
        self.assertEqual(report.metrics.unnecessary_human_interruption_rate, 0.0)
