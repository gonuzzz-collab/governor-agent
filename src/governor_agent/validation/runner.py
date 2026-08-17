"""Purpose-built validators with no generic shell execution surface."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from governor_agent.adapters import GovernanceSourceError, ValidatorKind, ValidatorSpec
from governor_agent.domain import ChangeRequest, ValidationResult, ValidationStatus


class ApprovedValidatorRunner:
    """Run only schema-approved validator kinds inside a confined project root."""

    def __init__(self, project_root: Path) -> None:
        if project_root.is_symlink():
            raise GovernanceSourceError("project root must not be a symlink")
        self._project_root = project_root.resolve(strict=True)

    def run(self, spec: ValidatorSpec, request: ChangeRequest) -> ValidationResult:
        if spec.kind is ValidatorKind.FILES_EXIST:
            return self._files_exist(spec, request)
        if spec.kind is ValidatorKind.PYTHON_UNITTEST:
            return self._python_unittest(spec)
        raise GovernanceSourceError(f"unsupported validator kind: {spec.kind}")

    def _files_exist(self, spec: ValidatorSpec, request: ChangeRequest) -> ValidationResult:
        missing: list[str] = []
        unsafe: list[str] = []
        for relative in request.files:
            try:
                resolved = self._confined_project_path(relative)
            except GovernanceSourceError:
                unsafe.append(relative)
                continue
            if not resolved.is_file():
                missing.append(relative)

        if unsafe:
            return ValidationResult(
                validator_id=spec.id,
                status=ValidationStatus.FAIL,
                summary="Requested files contain a symlink or path escape.",
            )
        if missing:
            return ValidationResult(
                validator_id=spec.id,
                status=ValidationStatus.FAIL,
                summary=f"{len(missing)} requested file(s) are missing.",
            )
        return ValidationResult(
            validator_id=spec.id,
            status=ValidationStatus.PASS,
            summary=f"All {len(request.files)} requested file(s) exist inside the project scope.",
            evidence_types=frozenset({"file-inspection"}),
        )

    def _python_unittest(self, spec: ValidatorSpec) -> ValidationResult:
        environment = {
            "PYTHONHASHSEED": "0",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONUNBUFFERED": "1",
        }
        try:
            completed = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                cwd=self._project_root,
                env=environment,
                capture_output=True,
                text=True,
                timeout=spec.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return ValidationResult(
                validator_id=spec.id,
                status=ValidationStatus.ERROR,
                summary="Approved Python unittest validator timed out.",
            )
        status = ValidationStatus.PASS if completed.returncode == 0 else ValidationStatus.FAIL
        return ValidationResult(
            validator_id=spec.id,
            status=status,
            summary=(
                "Approved Python unittest validator passed."
                if status is ValidationStatus.PASS
                else "Approved Python unittest validator failed; raw output is withheld from logs."
            ),
            evidence_types=(
                frozenset({"test-results"}) if status is ValidationStatus.PASS else frozenset()
            ),
        )

    def _confined_project_path(self, relative: str) -> Path:
        candidate = self._project_root / relative
        current = candidate
        while current != self._project_root:
            if current.is_symlink():
                raise GovernanceSourceError(f"symlink is forbidden in project path: {relative}")
            current = current.parent
        resolved = candidate.resolve(strict=False)
        try:
            resolved.relative_to(self._project_root)
        except ValueError as exc:
            raise GovernanceSourceError(f"project path escapes scope: {relative}") from exc
        return resolved
