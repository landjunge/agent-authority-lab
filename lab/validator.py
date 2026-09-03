"""Composition validator for Agent Authority Lab v0.2.

Delegation convention
---------------------
Root actor depth is **0**. A successful `delegate` from that actor assigns the
target depth **1**. A further `delegate` (A→B) would be depth **2** and is
rejected by I4 (`delegation_depth <= 1`). So root→A is allowed; the next
unauthorized delegation step is denied.

Trusted path: predict → evaluate invariants → ALLOW/DENY. No LLM.
Denied requests do not mutate workflow state.

Registry lock order
-------------------
`_table_lock` then `_WorkflowEntry.lock`. Never the reverse. `_table_lock` is
held only for dict lookup / admit / pop — never across predict/evaluate, and
never while waiting for an entry lock. See
`docs/PHASE1-WORKFLOW-LIFECYCLE-ATOMICITY.md`.

`finish()` is a trusted coordinator/lifecycle API, not an agent action. An
agent able to call it could drop its own budget and provenance.
"""

from __future__ import annotations

import threading

from lab.invariants import evaluate
from lab.models import (
    CAPACITY_EXCEEDED,
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


class _WorkflowEntry:
    """One registry identity: the lock and the state cannot exist apart."""

    __slots__ = ("lock", "state", "retired")

    def __init__(self, state: WorkflowState) -> None:
        self.lock = threading.Lock()
        self.state = state
        self.retired = False


class Lab:
    #: Beyond this many concurrently tracked workflows, `submit` refuses rather
    #: than growing without bound. A monitor that dies of memory exhaustion is
    #: fail-crash, not fail-closed, and an unbounded table is reachable by
    #: anyone who can pick workflow ids. Call `finish()` when a workflow ends.
    MAX_TRACKED_WORKFLOWS = 10_000

    def __init__(self, max_tracked: int | None = None) -> None:
        self._entries: dict[str, _WorkflowEntry] = {}
        self._table_lock = threading.Lock()
        self._max_tracked = (
            self.MAX_TRACKED_WORKFLOWS if max_tracked is None else max_tracked
        )

    @property
    def _states(self) -> dict[str, WorkflowState]:
        """Test/debug view of live state. Not a second registry."""
        with self._table_lock:
            return {wid: e.state for wid, e in self._entries.items()}

    @property
    def _locks(self) -> dict[str, threading.Lock]:
        """Test/debug view of live locks. Not a second registry."""
        with self._table_lock:
            return {wid: e.lock for wid, e in self._entries.items()}

    def _capacity_seam(self, workflow_id: str) -> None:
        """Test hook. After a negative capacity check, before reservation.

        Production is a no-op. Tests assign a callable that barriers here so
        both threads pass the check before either reserves. The admission
        protocol must remain correct even when this hook stalls.
        """

    def _after_lock_ref(self, workflow_id: str, lock: threading.Lock) -> None:
        """Test hook. After obtaining the per-workflow lock object, before acquire.

        Production is a no-op. Tests stall here to let finish() unregister the
        entry while submit() still holds only a reference.
        """

    def _inside_submit_locked(self, workflow_id: str) -> None:
        """Test hook. Called once the per-workflow lock is held, before predict.

        Production is a no-op. Tests barrier here across distinct workflow ids
        to prove the table lock is not held for the whole submit.
        """

    def _finish_holding_after_state_removed(self, workflow_id: str) -> None:
        """Test hook. Entry unregistered, per-workflow lock held, retired set.

        Production is a no-op.
        """

    def _lock_for(self, workflow_id: str) -> threading.Lock:
        """Historical helper. finish() and state() must not call this.

        Stage 1 instruments this to prove finish("unknown") does not mint.
        Admission goes through `_admit`.
        """
        entry = self._admit(workflow_id)
        if entry is None:
            raise RuntimeError("capacity exceeded")
        return entry.lock

    def _at_capacity(self, workflow_id: str) -> bool:
        with self._table_lock:
            return (
                workflow_id not in self._entries
                and len(self._entries) >= self._max_tracked
            )

    def _admit(self, workflow_id: str) -> _WorkflowEntry | None:
        """Atomically return a live entry, reserve a new one, or reject at cap.

        Checking capacity, inserting the entry, and binding its lock are one
        critical section under `_table_lock`.
        """
        with self._table_lock:
            entry = self._entries.get(workflow_id)
            if entry is not None:
                return entry
            if len(self._entries) >= self._max_tracked:
                return None
            entry = _WorkflowEntry(empty_state(workflow_id))
            self._entries[workflow_id] = entry
            return entry

    def finish(self, workflow_id: str) -> bool:
        """Drop all state for a completed workflow. Returns True if it existed.

        Trusted coordinator API, not an agent action. Unknown ids must not
        mint an entry. The entry is removed from the registry before waiters
        on its lock proceed; waiters must observe `retired` and not write.
        """
        with self._table_lock:
            entry = self._entries.pop(workflow_id, None)
        if entry is None:
            return False
        with entry.lock:
            entry.retired = True
            self._finish_holding_after_state_removed(workflow_id)
            return True

    def tracked_workflows(self) -> int:
        with self._table_lock:
            return len(self._entries)

    def _state_unlocked(self, workflow_id: str) -> WorkflowState:
        """Caller holds the live entry lock. Does not allocate."""
        entry = self._entries.get(workflow_id)
        if entry is None or entry.retired:
            raise RuntimeError(f"no live entry for {workflow_id!r}")
        return entry.state

    def state(self, workflow_id: str) -> WorkflowState:
        """Public view: a detached snapshot. Mutating it does not affect the monitor.

        Unknown ids return an empty snapshot without storing state or a lock.
        Known ids snapshot under the per-workflow lock.
        """
        with self._table_lock:
            entry = self._entries.get(workflow_id)
        if entry is None:
            return empty_state(workflow_id).snapshot()
        with entry.lock:
            if entry.retired:
                return empty_state(workflow_id).snapshot()
            return entry.state.snapshot()

    def submit(self, req: ActionRequest) -> Decision:
        if validate_request(req) is not None:
            return Decision(
                allow=False,
                deny_reason=INVALID_REQUEST,
                violated_invariants=[INVALID_REQUEST],
            )
        while True:
            if self._at_capacity(req.workflow_id):
                return Decision(
                    allow=False,
                    deny_reason=CAPACITY_EXCEEDED,
                    violated_invariants=[CAPACITY_EXCEEDED],
                )
            self._capacity_seam(req.workflow_id)
            entry = self._admit(req.workflow_id)
            if entry is None:
                return Decision(
                    allow=False,
                    deny_reason=CAPACITY_EXCEEDED,
                    violated_invariants=[CAPACITY_EXCEEDED],
                )
            self._after_lock_ref(req.workflow_id, entry.lock)
            with entry.lock:
                if entry.retired:
                    # finish() unregistered this identity while we held only a
                    # reference. Retry against a clean generation — do not write.
                    continue
                return self._submit_locked(entry, req)

    def _submit_locked(self, entry: _WorkflowEntry, req: ActionRequest) -> Decision:
        self._inside_submit_locked(req.workflow_id)
        current = entry.state
        before = current.snapshot()
        predicted = predict_next(before, req)
        violated = evaluate(req, predicted)
        if violated:
            # Identity: the live object was never mutated; keep the snapshot.
            entry.state = before
            return Decision(
                allow=False,
                deny_reason=violated[0],
                violated_invariants=list(violated),
            )
        rec = record(req=req, before=before, after=predicted, decision="ALLOW")
        predicted.provenance.append(rec)
        entry.state = predicted
        return Decision(allow=True, deny_reason=None, violated_invariants=[])
