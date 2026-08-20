from __future__ import annotations

import unittest
from datetime import datetime

from pydantic import ValidationError

from governor_agent.domain.models import (
    AuthorityRegistry,
    ChangePermit,
    ChangeRequest,
    Policy,
    PolicyKind,
)
from governor_agent.domain.paths import UnsafePathError, matches_patterns, validate_relative_path


class PathContractTests(unittest.TestCase):
    def test_valid_path_matches_allowed_glob(self) -> None:
        self.assertTrue(matches_patterns("src/auth/service/token.py", ("src/auth/**",)))

    def test_parent_escape_is_rejected(self) -> None:
        with self.assertRaises(UnsafePathError):
            validate_relative_path("../private.env")

    def test_absolute_path_is_rejected(self) -> None:
        with self.assertRaises(UnsafePathError):
            validate_relative_path("/etc/passwd")

    def test_backslash_path_is_rejected(self) -> None:
        with self.assertRaises(UnsafePathError):
            validate_relative_path("src\\escape.py")


class SchemaContractTests(unittest.TestCase):
    def test_change_request_rejects_extra_fields(self) -> None:
        with self.assertRaises(ValidationError):
            ChangeRequest.model_validate(
                {
                    "id": "req-1",
                    "project": "demo",
                    "objective": "safe change",
                    "actor": "builder",
                    "capability": "code-change",
                    "requested_scope": ["src/**"],
                    "files": ["src/app.py"],
                    "unexpected_authority": "admin",
                }
            )

    def test_change_request_rejects_duplicate_files(self) -> None:
        with self.assertRaises(ValidationError):
            ChangeRequest(
                id="req-1",
                project="demo",
                objective="safe change",
                actor="builder",
                capability="code-change",
                requested_scope=("src/**",),
                files=("src/app.py", "src/app.py"),
            )

    def test_policy_requires_kind_specific_fields(self) -> None:
        with self.assertRaises(ValidationError):
            Policy(
                id="policy-1",
                kind=PolicyKind.PERSISTENCE_OWNERSHIP,
                description="One source of truth.",
            )

    def test_permit_expiry_must_include_timezone(self) -> None:
        with self.assertRaises(ValidationError):
            ChangePermit(
                permit_id="permit-1",
                request_id="req-1",
                capability="code-change",
                actor="builder",
                allowed_actions=frozenset({"change"}),
                allowed_paths=("src/**",),
                environment="local",
                expires_at=datetime(2026, 8, 20),
                rollback="Revert the file change.",
            )

    def test_authority_registry_rejects_duplicate_actors(self) -> None:
        with self.assertRaisesRegex(ValidationError, "duplicate actors"):
            AuthorityRegistry.model_validate(
                {
                    "schema_version": "governor.authority-registry.v1",
                    "authorities": [
                        {"actor": "builder"},
                        {"actor": "builder"},
                    ],
                }
            )


if __name__ == "__main__":
    unittest.main()
