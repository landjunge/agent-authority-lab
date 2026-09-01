"""Deterministic path identity. No filesystem, no OS-specific case folding."""

from __future__ import annotations


def canonical_path(raw: str) -> str:
    text = str(raw or "").replace("\\", "/")
    parts: list[str] = []
    for part in text.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if parts:
                parts.pop()
            continue
        parts.append(part)
    return "/".join(parts)


def is_protected_path(raw: str, protected: str) -> bool:
    return canonical_path(raw) == canonical_path(protected)


def is_security_test_path(raw: str) -> bool:
    """v0.3 identities only: tests/test_security.py or anything under tests/security/."""
    c = canonical_path(raw)
    if c == "tests/test_security.py":
        return True
    return c == "tests/security" or c.startswith("tests/security/")
