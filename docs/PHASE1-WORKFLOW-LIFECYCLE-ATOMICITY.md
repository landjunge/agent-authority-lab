# Phase 1 repair — workflow registry atomicity

Additive. Does **not** rewrite v0.2–v0.5 or Phase 2 experiment specs. Not Experiment 04. Not Defect C (`finish("unknown")` / `state("unknown")` must not allocate — Stage 1, already landed).

Two in-process races in the workflow table:

**Defect A.** `_at_capacity()` took the table lock, released it, then `_lock_for()` took it again. Two threads with new ids could both pass the check before either reserved. Sequential overflow tests stayed green. Forcing a seam between check and reserve admitted both workflows at `max_tracked=1`.

**Defect B.** `submit()` obtained a lock *reference* from `_lock_for()` and had not yet acquired it. `finish()` then removed that lock from the registry. The waiting `submit()` proceeded on the stale object, created state with no registry lock, and a later `_lock_for()` minted a second lock for the same id. Per-workflow submit atomicity for that id was gone.

**Defect D** (torn `state()` snapshot) was checked in Stage 1 verification and is **not** present: `state()` still acquires the per-workflow lock for known ids.

## Rules

1. One registry entry per live workflow id. The per-workflow lock and the `WorkflowState` are fields of that entry. They cannot be inserted or removed independently.
2. Checking capacity, reserving a new workflow, and binding its lock are one critical section under `_table_lock`.
3. `tracked_workflows()` never exceeds `max_tracked`, including under concurrent new ids.
4. At most one active registry entry per workflow id at any time.
5. No thread may use a stale (already removed) lock reference to create state. Waiters on a retired entry retry admission; they do not write.
6. `submit()` and `finish()` have one documented order (below).
7. After a completed `finish()`, the same id starts clean (`action_count == 0`, no provenance).
8. Existing workflows keep working at full capacity. `CAPACITY_EXCEEDED` applies only to *new* ids.
9. `CAPACITY_EXCEEDED` creates no state, no lock, no provenance.
10. Distinct workflow ids still proceed in parallel: `_table_lock` is not held across predict/evaluate.
11. Stage 1 holds: `state()` and `finish()` allocate nothing for unknown ids. `state()` on a known id still snapshots under the per-workflow lock.

### `finish()` is not an agent action

`Lab.finish(workflow_id)` is a **trusted coordinator / lifecycle API**. It is not in `KNOWN_ACTIONS` and is not evaluated by I1–I9. An agent able to call it could drop its own `action_count`, unique-file set and provenance and continue as a new workflow. That would be a budget reset, not a composition-monitor decision. Callers of `finish` are the test harness and a future trusted supervisor. This is a security property of the lab boundary, not an invariant.

### Lock order

1. `_table_lock` protects `_entries` (the dict). Hold it only for lookup, admit, pop, and `tracked_workflows`.
2. `_WorkflowEntry.lock` protects that entry's `state` and `retired`.
3. **Never** acquire `_table_lock` while holding an entry lock. That order is what makes `finish()` pop the dict first, then wait for in-flight `submit()` without deadlocking admission of *other* ids.
4. Test seams (`_capacity_seam`, `_after_lock_ref`, `_inside_submit_locked`, `_finish_holding_after_state_removed`) are no-ops in production. They must not be used to skip reservation. Admission remains correct if a seam stalls.

### Why double registration is impossible

`_admit` is the only inserter. Under `_table_lock` it either returns the existing entry, rejects at capacity, or inserts exactly one new `_WorkflowEntry`. Two threads for the same new id serialize on `_table_lock`; the second sees the first's entry. Two threads for different new ids at capacity: the second sees `len(_entries) >= max_tracked` and returns `None`.

### Why orphaned locks are impossible

There is no lock table separate from `_entries`. `finish()` pops the entry from the dict *before* waiters on that entry's lock proceed. A waiter that still holds the Python object acquires the lock, observes `retired is True`, and retries `_admit` instead of writing. A later `_admit` for the same id creates a new entry (new lock, empty state). The stale object is not in the registry and cannot be reused as a live identity.

### `submit` / `finish` order

```text
submit:  invalid? → (loop) capacity check → capacity_seam → admit
         → after_lock_ref → entry.lock → if retired: retry
         → predict → evaluate → commit or DENY-restore
finish:  table_lock: pop entry (or return False if absent)
         → entry.lock → retired = True → release
```

A `submit` that lost the race with `finish` never writes into the popped entry. It retries; after `finish` returns, the id is a new generation or `CAPACITY_EXCEEDED`.

## Acceptance

- Two threads, new ids, `max_tracked=1`, barrier in `_capacity_seam` after the first capacity check: exactly one ALLOW, one DENY `CAPACITY_EXCEEDED`, `tracked_workflows() == 1`, `_states` keys == `_locks` keys. Seam invoked twice.
- `submit` has the lock reference and is stalled in `_after_lock_ref`; `finish` then unregisters. `submit` still ALLOW on a clean generation; state and lock remain paired; `action_count == 1`. Both hooks reached.
- Distinct ids barrier inside the per-workflow critical section without timeout.
- Sequential overflow still creates no state/lock/provenance for the rejected id.
- Existing id at capacity still ALLOW.
- Stage 1 tests still green. Frozen tests unmodified.

## Out of scope

- Defect C (Stage 1)
- PBT-P5 / I2 verb incompleteness (`file.create` still bypasses the unique-file cap — recorded as OOS-019, not fixed)
- Multi-process / distributed monitors (OOS-011)
- Access control that would prevent an agent from importing `Lab` and calling `finish` (the Python object is the TCB)
- Experiment 04
