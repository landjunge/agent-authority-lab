# Phase 1 repair — public state is a snapshot

Additive. Does **not** rewrite v0.2–v0.5. Not Experiment 04.

`Lab.state()` returned the live `WorkflowState`. Callers could zero `action_count` and clear provenance, then the 101st action ALLOW. `snapshot()` copied the provenance list but shared `ProvenanceRecord` objects.

## Rules

1. Public `state(workflow_id)` returns `snapshot()` of the internal object, under the same per-workflow lock as `submit`.
2. `submit` uses private `_state_unlocked()` for the live object.
3. `snapshot()` copies provenance records (new objects). `ProvenanceRecord` is frozen.
4. Mutating the object returned by `state()` must not change the next `submit` decision.

## Acceptance

- After 100 ALLOW writes of one path, `lab.state(wid).action_count = 0` and `.provenance.clear()`; the next write is DENY `I1_ACTION_BUDGET`; live `action_count` stays 100.
- After one ALLOW, assigning `lab.state(wid).provenance[0].action = "tampered"` does not change the internal record (frozen or copy).
- Frozen tests unmodified and green.

## Out of scope

- Phase 2 holdings encapsulation
- Cryptographic integrity of provenance
