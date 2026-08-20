"""Read-only adapter for the public synthetic factory fixture."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel, TypeAdapter, ValidationError

from governor_agent.adapters.contracts import (
    FactoryManifest,
    GoldenPathDocument,
    GovernanceSourceError,
    ValidatorUnavailableError,
    ValidatorSpec,
)
from governor_agent.domain import (
    AuthorityGrant,
    AuthorityRegistry,
    Capability,
    CapabilityRegistry,
    ChangePermit,
    ChangeRequest,
    Policy,
)

T = TypeVar("T", bound=BaseModel)
MAX_GOVERNANCE_FILE_BYTES = 1_000_000


class SyntheticFactoryAdapter:
    """Load schema-validated governance from a fixed, public fixture layout."""

    def __init__(self, root: Path) -> None:
        if root.is_symlink():
            raise GovernanceSourceError("factory root must not be a symlink")
        self._root = root.resolve(strict=True)
        if not self._root.is_dir():
            raise GovernanceSourceError("factory root must be a directory")
        self._manifest = self._read_model("factory.json", FactoryManifest)
        self._project_root = self._resolve_confined(self._manifest.project_path, require_dir=True)

    @property
    def project_root(self) -> Path:
        return self._project_root

    def get_golden_path(self) -> GoldenPathDocument:
        return self._read_model("golden_path.json", GoldenPathDocument)

    def get_capability(self, capability_id: str) -> Capability:
        registry = self._read_model("capabilities.json", CapabilityRegistry)
        matches = [
            capability for capability in registry.capabilities if capability.id == capability_id
        ]
        if len(matches) != 1:
            raise GovernanceSourceError(
                f"expected exactly one Capability with id={capability_id!r}"
            )
        return matches[0]

    def get_authority(self, actor: str) -> AuthorityGrant:
        registry = self._read_model("authorities.json", AuthorityRegistry)
        matches = [authority for authority in registry.authorities if authority.actor == actor]
        if len(matches) != 1:
            raise GovernanceSourceError(f"expected exactly one AuthorityGrant with actor={actor!r}")
        return matches[0]

    def get_policies(self, request: ChangeRequest) -> tuple[Policy, ...]:
        del request
        return self._read_models("policies.json", Policy)

    def get_permit(self, request_id: str) -> ChangePermit | None:
        matches = [
            permit
            for permit in self._read_models("permits.json", ChangePermit)
            if permit.request_id == request_id
        ]
        if len(matches) > 1:
            raise GovernanceSourceError(f"duplicate permit for request: {request_id}")
        return matches[0] if matches else None

    def get_validator(self, validator_id: str) -> ValidatorSpec:
        matches = [
            item
            for item in self._read_models("validators.json", ValidatorSpec)
            if item.id == validator_id
        ]
        if len(matches) != 1:
            raise ValidatorUnavailableError(
                f"expected exactly one ValidatorSpec with id={validator_id!r}"
            )
        return matches[0]

    def _find_one(
        self,
        filename: str,
        model: type[T],
        field: str,
        expected: str,
    ) -> T:
        matches = [
            item for item in self._read_models(filename, model) if getattr(item, field) == expected
        ]
        if len(matches) != 1:
            raise GovernanceSourceError(
                f"expected exactly one {model.__name__} with {field}={expected!r}"
            )
        return matches[0]

    def _read_model(self, filename: str, model: type[T]) -> T:
        try:
            return model.model_validate(self._read_json(filename))
        except ValidationError as exc:
            raise GovernanceSourceError(f"invalid {filename}: {exc}") from exc

    def _read_models(self, filename: str, model: type[T]) -> tuple[T, ...]:
        try:
            adapter: TypeAdapter[list[T]] = TypeAdapter(list[model])  # type: ignore[valid-type]
            return tuple(adapter.validate_python(self._read_json(filename)))
        except ValidationError as exc:
            raise GovernanceSourceError(f"invalid {filename}: {exc}") from exc

    def _read_json(self, filename: str) -> Any:
        path = self._resolve_confined(filename)
        if path.stat().st_size > MAX_GOVERNANCE_FILE_BYTES:
            raise GovernanceSourceError(f"governance file exceeds size limit: {filename}")
        try:
            with path.open("r", encoding="utf-8") as stream:
                return json.load(stream)
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise GovernanceSourceError(f"cannot read governance file {filename}: {exc}") from exc

    def _resolve_confined(self, relative: str, *, require_dir: bool = False) -> Path:
        candidate = self._root / relative
        current = candidate
        while current != self._root:
            if current.is_symlink():
                raise GovernanceSourceError(f"symlink is forbidden in factory path: {relative}")
            current = current.parent
        try:
            resolved = candidate.resolve(strict=True)
            resolved.relative_to(self._root)
        except (FileNotFoundError, ValueError) as exc:
            raise GovernanceSourceError(f"factory path escapes or is missing: {relative}") from exc
        if require_dir and not resolved.is_dir():
            raise GovernanceSourceError(f"factory project path is not a directory: {relative}")
        if not require_dir and not resolved.is_file():
            raise GovernanceSourceError(f"governance path is not a file: {relative}")
        return resolved
