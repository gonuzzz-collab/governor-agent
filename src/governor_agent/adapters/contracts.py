"""Contracts that isolate Governor from any particular software factory layout."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, field_validator

from governor_agent.domain import (
    AuthorityGrant,
    Capability,
    ChangePermit,
    ChangeRequest,
    Policy,
)
from governor_agent.domain.paths import validate_relative_path


class GovernanceSourceError(RuntimeError):
    """Raised when trusted governance data cannot satisfy its declared contract."""


class ValidatorUnavailableError(GovernanceSourceError):
    """Raised when a named validator has no unique approved definition."""


class ValidatorKind(str, Enum):
    FILES_EXIST = "files_exist"
    PYTHON_UNITTEST = "python_unittest"


MODEL_CONFIG = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class FactoryManifest(BaseModel):
    model_config = MODEL_CONFIG

    factory_id: str = Field(min_length=1)
    project_path: str = Field(min_length=1)

    @field_validator("project_path")
    @classmethod
    def validate_project_path(cls, value: str) -> str:
        return validate_relative_path(value)


class GoldenPathDocument(BaseModel):
    model_config = MODEL_CONFIG

    id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    normative_sources: tuple[str, ...] = Field(min_length=1)
    required_sequence: tuple[str, ...] = Field(min_length=1)
    notes: tuple[str, ...] = ()


class ValidatorSpec(BaseModel):
    model_config = MODEL_CONFIG

    id: str = Field(min_length=1)
    kind: ValidatorKind
    timeout_seconds: int = Field(default=20, ge=1, le=60)


class GovernanceSource(Protocol):
    """Factory-independent, read-only governance source."""

    @property
    def project_root(self) -> Path: ...

    def get_golden_path(self) -> GoldenPathDocument: ...

    def get_capability(self, capability_id: str) -> Capability: ...

    def get_authority(self, actor: str) -> AuthorityGrant: ...

    def get_policies(self, request: ChangeRequest) -> tuple[Policy, ...]: ...

    def get_permit(self, request_id: str) -> ChangePermit | None: ...

    def get_validator(self, validator_id: str) -> ValidatorSpec: ...
