"""Local append-only audit storage for Observer-mode Governor runs."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from governor_agent.domain import ChangeRequest, GovernanceDecision, ValidationResult

MAX_AUDIT_RECORD_BYTES = 5_000_000


class AuditIntegrityError(RuntimeError):
    """Raised when an audit record is malformed, out of scope, or has been altered."""


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
        unsigned = AuditRecord.model_validate({**payload, "record_digest": f"sha256:{'0' * 64}"})
        unsigned_payload = unsigned.model_dump(mode="json", exclude={"record_digest"})
        record = unsigned.model_copy(
            update={"record_digest": f"sha256:{self._payload_digest(unsigned_payload)}"}
        )

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

    def verify(self, path: Path) -> AuditRecord:
        """Load and verify a record confined to this store's runs directory."""

        if path.is_symlink():
            raise AuditIntegrityError("audit record must not be a symlink")
        runs_root = (self._root / "runs").resolve(strict=True)
        try:
            resolved = path.resolve(strict=True)
            resolved.relative_to(runs_root)
        except (FileNotFoundError, ValueError) as exc:
            raise AuditIntegrityError("audit record is missing or outside the audit store") from exc
        if not resolved.is_file():
            raise AuditIntegrityError("audit record is not a file")
        if resolved.stat().st_size > MAX_AUDIT_RECORD_BYTES:
            raise AuditIntegrityError("audit record exceeds size limit")
        try:
            with resolved.open("r", encoding="utf-8") as stream:
                raw_payload = json.load(stream)
            record = AuditRecord.model_validate(raw_payload)
        except (OSError, UnicodeError, json.JSONDecodeError, ValidationError) as exc:
            raise AuditIntegrityError(f"invalid audit record: {exc}") from exc
        unsigned_payload = dict(raw_payload)
        unsigned_payload.pop("record_digest", None)
        expected = f"sha256:{self._payload_digest(unsigned_payload)}"
        if not hmac.compare_digest(record.record_digest, expected):
            raise AuditIntegrityError("audit record digest mismatch")
        return record

    @staticmethod
    def _payload_digest(payload: dict[str, object]) -> str:
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
