from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock


@dataclass(frozen=True)
class AuditEvent:
    timestamp: str
    event: str
    workflow_id: str
    agent_id: str
    fingerprint: str
    reason: str


class AuditLedger:
    """Append-only in-process ledger. Durable tamper evidence is a future boundary."""

    def __init__(self):
        self._lock = RLock()
        self._events: list[AuditEvent] = []

    def append(self, event: str, workflow_id: str, agent_id: str, fingerprint: str, reason: str) -> None:
        with self._lock:
            self._events.append(AuditEvent(
                datetime.now(timezone.utc).isoformat(), event, workflow_id, agent_id, fingerprint, reason
            ))

    def events(self) -> tuple[AuditEvent, ...]:
        with self._lock:
            return tuple(self._events)
