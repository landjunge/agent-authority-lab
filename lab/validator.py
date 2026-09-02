"""Composition validator for Agent Authority Lab v0.2.

Delegation convention
---------------------
Root actor depth is **0**. A successful `delegate` from that actor assigns the
target depth **1**. A further `delegate` (A→B) would be depth **2** and is
rejected by I4 (`delegation_depth <= 1`). So root→A is allowed; the next
unauthorized delegation step is denied.

Trusted path: predict → evaluate invariants → ALLOW/DENY. No LLM.
Denied requests do not mutate workflow state.
"""

from __future__ import annotations

import threading

from lab.invariants import evaluate
from lab.models import (
    INVALID_REQUEST,
    MAX_REQUEST_FIELD,
    ActionRequest,
    Decision,
    WorkflowState,
)
from lab.provenance import record
from lab.state import empty_state, predict_next


def validate_request(req: object) -> str | None:
    """Return INVALID_REQUEST if `req` is not a usable ActionRequest. Else None."""
    if not isinstance(req, ActionRequest):
        return INVALID_REQUEST
    for name in ("actor", "action", "resource", "workflow_id"):
        val = getattr(req, name, None)
        if not isinstance(val, str) or not val or len(val) > MAX_REQUEST_FIELD:
            return INVALID_REQUEST
    if not isinstance(req.parameters, dict):
        return INVALID_REQUEST
    return None


class Lab:
    def __init__(self) -> None:
        self._states: dict[str, WorkflowState] = {}
        self._locks: dict[str, threading.Lock] = {}
        self._table_lock = threading.Lock()

    def _lock_for(self, workflow_id: str) -> threading.Lock:
        with self._table_lock:
            lock = self._locks.get(workflow_id)
            if lock is None:
                lock = threading.Lock()
                self._locks[workflow_id] = lock
            return lock

    def state(self, workflow_id: str) -> WorkflowState:
        if workflow_id not in self._states:
            self._states[workflow_id] = empty_state(workflow_id)
        return self._states[workflow_id]

    def submit(self, req: ActionRequest) -> Decision:
        if validate_request(req) is not None:
            return Decision(
                allow=False,
                deny_reason=INVALID_REQUEST,
                violated_invariants=[INVALID_REQUEST],
            )
        lock = self._lock_for(req.workflow_id)
        with lock:
            current = self.state(req.workflow_id)
            before = current.snapshot()
            predicted = predict_next(before, req)
            violated = evaluate(req, predicted)
            if violated:
                # Identity: the live object was never mutated; keep the snapshot.
                self._states[req.workflow_id] = before
                return Decision(
                    allow=False,
                    deny_reason=violated[0],
                    violated_invariants=list(violated),
                )
            rec = record(req=req, before=before, after=predicted, decision="ALLOW")
            predicted.provenance.append(rec)
            self._states[req.workflow_id] = predicted
            return Decision(allow=True, deny_reason=None, violated_invariants=[])
