"""Local append-only audit storage for Observer-mode Governor runs."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from governor_agent.domain import ChangeRequest, GovernanceDecision, ValidationResult


class AuditRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: str = Field(pattern=r"^run-[0-9a-f]{32}$")
    recorded_at: datetime
    request: ChangeRequest
    decision: GovernanceDecision
    validations: tuple[ValidationResult, ...]
    record_digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")


class AuditStore:
    """Persist unique run records without overwriting prior governance evidence."""

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def record(
        self,
        request: ChangeRequest,
        decision: GovernanceDecision,
        validations: tuple[ValidationResult, ...],
    ) -> tuple[AuditRecord, Path]:
        run_id = f"run-{uuid.uuid4().hex}"
        recorded_at = datetime.now(timezone.utc)
        payload = {
            "run_id": run_id,
            "recorded_at": recorded_at.isoformat(),
            "request": request.model_dump(mode="json"),
            "decision": decision.model_dump(mode="json"),
            "validations": [item.model_dump(mode="json") for item in validations],
        }
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        record = AuditRecord.model_validate({**payload, "record_digest": f"sha256:{digest}"})

        directory = self._root / "runs"
        directory.mkdir(parents=True, exist_ok=True)
        destination = directory / f"{run_id}.json"
        descriptor, temporary_name = tempfile.mkstemp(prefix=".governor-", dir=directory)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                json.dump(record.model_dump(mode="json"), stream, indent=2, sort_keys=True)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.link(temporary_name, destination)
        finally:
            Path(temporary_name).unlink(missing_ok=True)
        return record, destination
