from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DataValue:
    value_id: str
    label: str
    origin: str
    derived_from: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()
    # Fake-world only. Never read by FlowOK / explanations.
    payload: str = ""


@dataclass
class Phase2Decision:
    allow: bool
    authority_ok: bool
    flow_ok: bool
    reason: str | None
    explanation: dict | None = None
    value: DataValue | None = None
