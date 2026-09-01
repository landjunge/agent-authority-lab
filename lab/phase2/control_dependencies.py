"""Modeled control decisions. No payload inspection. No LLM."""

from __future__ import annotations

from dataclasses import dataclass

CONTROL_ORIGIN = "control://decision"


@dataclass(frozen=True)
class ControlDecision:
    decision_id: str
    depends_on: tuple[str, ...]
    label: str
    origin: str
