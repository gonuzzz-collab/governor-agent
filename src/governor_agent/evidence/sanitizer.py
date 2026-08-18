"""Local minimization, secret detection, pseudonymization, and path privacy."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable
from pathlib import Path

from governor_agent.evidence.models import (
    EvidenceBoundaryError,
    EvidenceDigest,
    EvidenceProvenance,
    EvidenceStatement,
    ExternalProcessingAction,
    FactValueKind,
    InformationClassification,
    RawEvidence,
    RedactionRecord,
    SanitizationAudit,
    SanitizationResult,
    SanitizedEvidence,
)
from governor_agent.evidence.policy import ExternalIntelligencePolicy

METADATA_KINDS = {
    FactValueKind.BOOLEAN,
    FactValueKind.COUNT,
    FactValueKind.ENUM,
    FactValueKind.HASH,
}


class SecretDetector:
    """Small fail-closed detector for critical secret shapes and secret-bearing paths."""

    PATTERNS = (
        ("aws_access_key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
        ("openai_token", re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b")),
        (
            "github_token",
            re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
        ),
        ("bearer_token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/-]{12,}=*")),
        ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
        (
            "credential_assignment",
            re.compile(
                r"(?i)\b(?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|passwd|secret)\b\s*[:=]\s*['\"]?[^\s'\"]{6,}"
            ),
        ),
        (
            "secret_path",
            re.compile(
                r"(?i)(?:^|[/\\])(?:\.env(?:\.[^/\\]+)?|auth\.json|credentials(?:\.[^/\\]+)?|\.ssh|\.aws)(?:$|[/\\])"
            ),
        ),
    )

    def detect(self, values: Iterable[str]) -> tuple[str, ...]:
        matches = {
            detector_id
            for value in values
            for detector_id, pattern in self.PATTERNS
            if pattern.search(value)
        }
        return tuple(sorted(matches))


class EvidenceSanitizer:
    """Transform one local RawEvidence object into a bounded external-safe representation."""

    PRIVATE_PATH = re.compile(r"(?<![A-Za-z0-9_])/(?:home|mnt|media|run/media)/[^\s'\"<>]+")
    WINDOWS_USER_PATH = re.compile(r"(?i)\b[A-Z]:\\Users\\[^\s'\"<>]+")

    def __init__(
        self,
        workspace_root: Path,
        *,
        policy: ExternalIntelligencePolicy | None = None,
        secret_detector: SecretDetector | None = None,
        private_identifiers: Iterable[str] = (),
    ) -> None:
        if workspace_root.is_symlink():
            raise EvidenceBoundaryError("evidence workspace root must not be a symlink")
        self._root = workspace_root.resolve(strict=True)
        if not self._root.is_dir():
            raise EvidenceBoundaryError("evidence workspace root must be a directory")
        self._policy = policy or ExternalIntelligencePolicy()
        self._detector = secret_detector or SecretDetector()
        default_private = {Path.home().name, self._root.name}
        self._private_identifiers = tuple(
            sorted({item for item in (*default_private, *private_identifiers) if len(item) >= 3})
        )

    def sanitize(self, raw: RawEvidence) -> SanitizationResult:
        detector_ids = self._detector.detect(self._secret_scan_values(raw))
        secret_detected = bool(detector_ids)
        effective_classification = (
            InformationClassification.SECRET if secret_detected else raw.classification
        )
        assessment = self._policy.evaluate(
            effective_classification,
            secret_detected=secret_detected,
        )
        logical_source = self._logical_source(raw.source_path, blocked=not assessment.allowed)
        statements: list[EvidenceStatement] = []
        digests: list[EvidenceDigest] = []
        redactions: list[RedactionRecord] = []
        retained: list[str] = []
        removed: list[str] = []

        for index, fact in enumerate(raw.facts):
            value = fact.value.get_secret_value()
            reason = self._removal_reason(
                fact.value_kind,
                fact.necessary,
                assessment.action,
            )
            if reason is not None:
                removed.append(fact.name)
                redactions.append(RedactionRecord(field=fact.name, reason=reason))
                if assessment.allowed and fact.value_kind in {
                    FactValueKind.CODE,
                    FactValueKind.FREE_TEXT,
                }:
                    digests.append(self._digest(fact.name, value))
                continue

            sanitized_value = self._sanitize_value(
                value,
                fact.value_kind,
                raw.classification,
                fact.name,
            )
            if sanitized_value != value:
                redactions.append(RedactionRecord(field=fact.name, reason="value_sanitized"))
            retained.append(fact.name)
            statements.append(
                EvidenceStatement(
                    statement_id=f"statement_{index + 1}",
                    kind=raw.kind,
                    name=fact.name,
                    value=sanitized_value,
                    value_kind=fact.value_kind,
                    trust_level=raw.trust_level,
                )
            )

        if not assessment.allowed:
            redactions.append(RedactionRecord(field="facts", reason="secret_blocked"))

        evidence = SanitizedEvidence(
            evidence_id=raw.evidence_id.replace("raw-", "ev-", 1),
            classification=effective_classification,
            project_alias=self._alias(
                "PROJECT",
                raw.local_project.get_secret_value(),
                public=raw.classification is InformationClassification.PUBLIC,
            ),
            component_alias=(
                self._alias(
                    "COMPONENT",
                    raw.local_component.get_secret_value(),
                    public=raw.classification is InformationClassification.PUBLIC,
                )
                if raw.local_component is not None
                else None
            ),
            event_type=raw.event_type,
            change_type=raw.change_type,
            statements=tuple(statements),
            applicable_policy_refs=raw.applicable_policy_refs,
            hashes=tuple(digests),
            redactions=tuple(redactions),
            provenance=EvidenceProvenance(
                source_type=raw.source_type,
                source_role=raw.source_role,
                trust_level=raw.trust_level,
                logical_source=logical_source,
            ),
            external_processing_allowed=assessment.allowed,
            external_processing_action=assessment.action,
            timestamp=raw.timestamp,
        )
        payload_digest = None
        if assessment.allowed:
            payload_digest = (
                "sha256:"
                + hashlib.sha256(
                    json.dumps(
                        evidence.model_dump(mode="json"),
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode("utf-8")
                ).hexdigest()
            )
        audit = SanitizationAudit(
            raw_evidence_id=raw.evidence_id,
            sanitized_evidence_id=evidence.evidence_id,
            original_classification=raw.classification,
            effective_classification=effective_classification,
            raw_fact_names=tuple(fact.name for fact in raw.facts),
            retained_fact_names=tuple(retained),
            removed_fact_names=tuple(removed),
            secret_detected=secret_detected,
            detector_ids=detector_ids,
            external_processing_action=assessment.action,
            external_processing_reason=assessment.reason,
            external_payload_digest=payload_digest,
        )
        return SanitizationResult(evidence=evidence, audit=audit)

    def _secret_scan_values(self, raw: RawEvidence) -> tuple[str, ...]:
        values = [raw.local_project.get_secret_value()]
        if raw.local_component is not None:
            values.append(raw.local_component.get_secret_value())
        if raw.source_path is not None:
            values.append(str(raw.source_path))
        values.extend(fact.value.get_secret_value() for fact in raw.facts)
        return tuple(values)

    def _logical_source(self, path: Path | None, *, blocked: bool) -> str:
        if blocked:
            return "factory://restricted-source"
        if path is None:
            return "factory://derived-observation"
        if path.is_symlink():
            raise EvidenceBoundaryError("raw evidence source must not be a symlink")
        try:
            relative = path.resolve(strict=True).relative_to(self._root)
        except (FileNotFoundError, ValueError) as exc:
            raise EvidenceBoundaryError("raw evidence source escapes the factory root") from exc
        if not path.is_file():
            raise EvidenceBoundaryError("raw evidence source must be a regular file")
        return f"factory://{relative.as_posix()}"

    @staticmethod
    def _removal_reason(
        kind: FactValueKind,
        necessary: bool,
        action: ExternalProcessingAction,
    ) -> str | None:
        if action is ExternalProcessingAction.BLOCK_EXTERNAL_EXPOSURE:
            return "secret_blocked"
        if not necessary:
            return "not_required"
        if kind is FactValueKind.CODE:
            return "code_minimized"
        if kind is FactValueKind.FREE_TEXT and action in {
            ExternalProcessingAction.ALLOW_SANITIZED,
            ExternalProcessingAction.ALLOW_METADATA_ONLY,
        }:
            return "free_text_minimized"
        if action is ExternalProcessingAction.ALLOW_METADATA_ONLY and kind not in METADATA_KINDS:
            return "metadata_only"
        return None

    def _sanitize_value(
        self,
        value: str,
        kind: FactValueKind,
        classification: InformationClassification,
        field_name: str,
    ) -> str:
        if kind is FactValueKind.PATH:
            return self._sanitize_path_value(value)
        if (
            kind is FactValueKind.IDENTIFIER
            and classification is not InformationClassification.PUBLIC
        ):
            return self._alias("VALUE", value, public=False)
        sanitized = self.PRIVATE_PATH.sub("[PRIVATE_PATH]", value)
        sanitized = self.WINDOWS_USER_PATH.sub("[PRIVATE_PATH]", sanitized)
        for identifier in self._private_identifiers:
            sanitized = re.sub(
                rf"(?<![A-Za-z0-9_]){re.escape(identifier)}(?![A-Za-z0-9_])",
                "[PRIVATE_ID]",
                sanitized,
            )
        sanitized = sanitized.strip()
        if not sanitized:
            return f"[{field_name.upper()}_REDACTED]"
        return sanitized[:2_000]

    def _sanitize_path_value(self, value: str) -> str:
        path = Path(value)
        if not path.is_absolute():
            normalized = path.as_posix().lstrip("./")
            if normalized and ".." not in Path(normalized).parts:
                return f"project://{normalized}"
        try:
            relative = path.resolve(strict=False).relative_to(self._root)
        except ValueError:
            return "project://[PRIVATE_PATH]"
        return f"project://{relative.as_posix()}"

    @staticmethod
    def _alias(prefix: str, value: str, *, public: bool) -> str:
        if public:
            normalized = re.sub(r"[^A-Z0-9]+", "_", value.upper()).strip("_")
            return f"PUBLIC_{normalized[:80] or 'RESOURCE'}"
        digest = hashlib.sha256(f"governor-evidence-v1\0{value}".encode()).hexdigest()[:12]
        return f"{prefix}_{digest.upper()}"

    @staticmethod
    def _digest(subject: str, value: str) -> EvidenceDigest:
        return EvidenceDigest(subject=subject, value=hashlib.sha256(value.encode()).hexdigest())
