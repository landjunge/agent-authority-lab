# Phase 1 repair — submit atomicity and malformed requests

Additive. Does **not** rewrite v0.2–v0.5 or Phase 2 experiment specs. Not Experiment 04. **Not T-19** (adapter raw vs canonical path remains documented debt).

ChatGPT reproduced: two threads, `action_count = 99`, both `submit` ALLOW, last writer wins. I1/I2/I4 and provenance are then lying. T-03/T-05 listed true concurrency as untested; OOS-011 is real distributed execution. This slice only serializes **in-process** `Lab.submit` for one `workflow_id`. It does not claim multi-process IFC.

## Rules

1. For each `workflow_id`, read → predict → evaluate → provenance → commit (or DENY restore) runs under **one lock**. Different workflows do not share that lock.
2. Malformed `ActionRequest` (wrong types, empty identity strings, `parameters is None`, overlong fields) is DENY `INVALID_REQUEST`. No exception from `submit` for those cases. State unchanged.
3. Field cap: `actor`, `action`, `resource`, `workflow_id` are `str`, length 1..256. `parameters` is a `dict`.
4. Frozen v0.2–v0.5 tests unmodified.

## Acceptance

- Two threads submitting the 100th unique write into a workflow at `action_count=99`: exactly one ALLOW, one DENY `I1_ACTION_BUDGET` (or I2 if that fires first), `action_count == 100`, `len(provenance) == action_count`.
- `parameters=None` on `repo.delete` → DENY `INVALID_REQUEST`, not `AttributeError`.
- DENY does not commit.

## Out of scope

- T-19 adapter identity
- Required GitHub status checks / pinning action SHAs
- Distributed / multi-process monitors
- Cryptographic tokens
