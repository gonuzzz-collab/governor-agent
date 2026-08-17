"""Append-only storage for agent evaluation reports."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from governor_agent.evaluation.models import EvaluationReport


class EvaluationStore:
    """Persist one immutable file per evaluation run."""

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def record(self, report: EvaluationReport) -> Path:
        directory = self._root / "evaluations"
        directory.mkdir(parents=True, exist_ok=True)
        destination = directory / f"{report.evaluation_id}.json"
        descriptor, temporary_name = tempfile.mkstemp(prefix=".evaluation-", dir=directory)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                json.dump(report.model_dump(mode="json"), stream, indent=2, sort_keys=True)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.link(temporary_name, destination)
        finally:
            Path(temporary_name).unlink(missing_ok=True)
        return destination
