"""Existing authoritative configuration store for the public demo."""

CONFIG_STORE: dict[str, str] = {"theme": "dark"}


def normalize_key(value: str) -> str:
    """Return the canonical configuration key."""

    return value.strip().lower().replace(" ", "-")
