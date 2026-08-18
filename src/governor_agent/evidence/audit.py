"""Append-only audit records that retain sanitized payloads but never raw values."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from governor_agent.domain import DecisionStatus
from governor_agent.domain.models import utc_now
from governor_agent.evidence.models import SanitizationAudit, SanitizedEvidence

MAX_EVIDENCE_AUDIT_BYTES = 1_000_000


class EvidenceAuditIntegrityError(RuntimeError):
    """An evidence audit record is malformed, altered, or outside its store."""


class EvidenceAuditRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    audit_id: str = Field(pattern=r"^evidence-audit-[0-9a-f]{32}$")
    recorded_at: datetime
    sanitization: SanitizationAudit
    external_payload: SanitizedEvidence
    codex_received: bool = False
    governor_decision: DecisionStatus | None = None
    record_digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")

    @model_validator(mode="after")
    def external_delivery_requires_permission(self) -> "EvidenceAuditRecord":
        if self.codex_received and not self.external_payload.external_processing_allowed:
            raise ValueError("blocked evidence cannot be recorded as delivered to Codex")
        return self


class EvidenceAuditStore:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    @property
    def root(self) -> Path:
        return self._root

    def record(
        self,
        sanitization: SanitizationAudit,
        external_payload: SanitizedEvidence,
        *,
        codex_received: bool = False,
        governor_decision: DecisionStatus | None = None,
    ) -> tuple[EvidenceAuditRecord, Path]:
        payload = {
            "audit_id": f"evidence-audit-{uuid.uuid4().hex}",
            "recorded_at": utc_now().isoformat(),
            "sanitization": sanitization.model_dump(mode="json"),
            "external_payload": external_payload.model_dump(mode="json"),
            "codex_received": codex_received,
            "governor_decision": governor_decision,
        }
        unsigned = EvidenceAuditRecord.model_validate(
            {**payload, "record_digest": f"sha256:{'0' * 64}"}
        )
        unsigned_payload = unsigned.model_dump(mode="json", exclude={"record_digest"})
        record = unsigned.model_copy(
            update={"record_digest": f"sha256:{self._payload_digest(unsigned_payload)}"}
        )

        directory = self._root / "evidence-runs"
        directory.mkdir(parents=True, exist_ok=True)
        destination = directory / f"{record.audit_id}.json"
        descriptor, temporary_name = tempfile.mkstemp(prefix=".evidence-", dir=directory)
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

    def verify(self, path: Path) -> EvidenceAuditRecord:
        if path.is_symlink():
            raise EvidenceAuditIntegrityError("evidence audit record must not be a symlink")
        runs_root = (self._root / "evidence-runs").resolve(strict=True)
        try:
            resolved = path.resolve(strict=True)
            resolved.relative_to(runs_root)
        except (FileNotFoundError, ValueError) as exc:
            raise EvidenceAuditIntegrityError(
                "evidence audit record is missing or outside the audit store"
            ) from exc
        if not resolved.is_file() or resolved.stat().st_size > MAX_EVIDENCE_AUDIT_BYTES:
            raise EvidenceAuditIntegrityError("evidence audit record is invalid or too large")
        try:
            payload = json.loads(resolved.read_text(encoding="utf-8"))
            record = EvidenceAuditRecord.model_validate(payload)
        except (OSError, UnicodeError, json.JSONDecodeError, ValidationError) as exc:
            raise EvidenceAuditIntegrityError("invalid evidence audit record") from exc
        unsigned_payload = dict(payload)
        unsigned_payload.pop("record_digest", None)
        expected = f"sha256:{self._payload_digest(unsigned_payload)}"
        if not hmac.compare_digest(record.record_digest, expected):
            raise EvidenceAuditIntegrityError("evidence audit record digest mismatch")
        return record

    @staticmethod
    def _payload_digest(payload: dict[str, object]) -> str:
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
