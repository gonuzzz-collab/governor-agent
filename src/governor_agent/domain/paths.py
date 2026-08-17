"""Pure, deterministic path rules used by governance gates."""

from __future__ import annotations

from fnmatch import fnmatchcase
from pathlib import PurePosixPath


class UnsafePathError(ValueError):
    """Raised when a requested path or path pattern is outside the safe contract."""


def validate_relative_path(value: str, *, allow_glob: bool = False) -> str:
    """Return a normalized repository-relative POSIX path or raise.

    This validation is intentionally lexical. Filesystem and symlink confinement is performed by
    the inspection layer before real files are accessed.
    """

    candidate = value.strip()
    if not candidate:
        raise UnsafePathError("path must not be empty")
    if "\x00" in candidate:
        raise UnsafePathError("path must not contain NUL")
    if "\\" in candidate:
        raise UnsafePathError("paths must use POSIX separators")
    if candidate.startswith(("/", "~")):
        raise UnsafePathError("path must be repository-relative")
    if "//" in candidate:
        raise UnsafePathError("path must not contain empty segments")
    if not allow_glob and any(character in candidate for character in "*?[]"):
        raise UnsafePathError("file paths must not contain glob syntax")

    raw_parts = candidate.split("/")
    if any(part in {"", ".", ".."} for part in raw_parts):
        raise UnsafePathError("path must not contain dot or parent segments")

    normalized = PurePosixPath(candidate).as_posix()
    if normalized in {"", "."}:
        raise UnsafePathError("path must identify a repository entry")
    return normalized


def matches_patterns(path: str, patterns: tuple[str, ...]) -> bool:
    """Return whether a validated path matches at least one validated pattern."""

    normalized = validate_relative_path(path)
    return any(
        fnmatchcase(normalized, validate_relative_path(item, allow_glob=True)) for item in patterns
    )
