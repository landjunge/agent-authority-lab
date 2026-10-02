from dataclasses import dataclass
from threading import RLock
from uuid import uuid4


@dataclass
class Approval:
    approval_id: str
    request_fingerprint: str
    approver: str
    consumed: bool = False


class ApprovalStore:
    """One approval authorizes one exact request fingerprint exactly once."""

    def __init__(self):
        self._lock = RLock()
        self._items: dict[str, Approval] = {}

    def issue(self, request_fingerprint: str, approver: str) -> Approval:
        with self._lock:
            item = Approval(str(uuid4()), request_fingerprint, approver)
            self._items[item.approval_id] = item
            return item

    def consume(self, approval_id: str, request_fingerprint: str) -> bool:
        with self._lock:
            item = self._items.get(approval_id)
            if not item or item.consumed or item.request_fingerprint != request_fingerprint:
                return False
            item.consumed = True
            return True
