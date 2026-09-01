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
    c = canonical_path(raw)
    if not c:
        return False
    parts = c.split("/")
    if parts[0] != "tests":
        return False
    if any(p == "security" for p in parts[:-1]):
        return True
    name = parts[-1]
    return name.startswith("test_") and "security" in name
