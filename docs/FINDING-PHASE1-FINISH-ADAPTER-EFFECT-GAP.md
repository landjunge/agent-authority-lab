# Finding — `finish()` can return before an already-authorized adapter effect

Status: **CONFIRMED**  
Scope: Phase 1 fake adapter / workflow lifecycle boundary  
Classification: lifecycle TOCTOU; authorization-to-effect atomicity gap  
Production impact: not established — the repository is a single-process fake lab

## Summary

`FakeAdapter.write()` first calls `Lab.submit()` and applies the repository
mutation only after the returned decision is `ALLOW`. The workflow lock protects
prediction, invariant evaluation, provenance and monitor-state commit. It does
not cover the subsequent adapter effect.

Consequently, a trusted coordinator can call `finish(workflow_id)` after the
monitor has committed `ALLOW` but before the adapter changes `FakeRepo`.
`finish()` returns `True`, removes the workflow state and provenance, and the
delayed adapter operation can still mutate the repository afterwards.

## Deterministic reproduction

`tests/test_finish_adapter_effect_atomicity_probe.py` replaces `Lab.submit` on
one adapter instance with a wrapper that pauses after the real `submit()` has
returned `ALLOW` and before `FakeAdapter.write()` receives that decision.
Threading events force this order without sleeps:

1. `write()` submits `file.write`.
2. `submit()` commits `ALLOW`; the wrapper pauses.
3. The coordinator calls `finish()`; it returns `True`.
4. The target path is still absent.
5. The wrapper releases the decision to `FakeAdapter.write()`.
6. The adapter writes the path after `finish()` completed.

The final assertion that no effect appears after completed `finish()` fails.

## Observed result

```text
FAILED test_no_adapter_effect_occurs_after_finish_returns
assert "src/late.py" not in adapter.repo.files
```

The failure is deterministic and was reproduced on `master` at `b35851f`.

## Security relevance

The monitor's state says that the workflow generation has ended, but an effect
authorized under that retired generation can become visible later. A future
real adapter could therefore perform a stale write after lifecycle cleanup.
The cleared state no longer contains the provenance row that authorized the
visible effect.

This does not bypass an invariant during `submit()` and does not invalidate the
existing registry-lock repair. It exposes a separate boundary between monitor
commit and effect commit.

## Classification constraints

- Not a v0.2 frozen-test failure: v0.2 does not specify an atomic adapter commit.
- Not a claim about a production or distributed runtime.
- Not caused by an agent calling `finish()`; the reproduction uses the trusted
  coordinator exactly as currently documented.
- No sleeps, network, real repository, credentials or external effects.

## Repair acceptance criteria

A future, separately authorized repair should define one lifecycle protocol in
which either:

1. an allowed adapter effect completes before `finish()` can return, or
2. a retired generation prevents the delayed effect from being applied.

The repair must also preserve:

- DENY never mutates `FakeRepo`;
- `finish("unknown")` allocates nothing;
- no stale entry can write monitor state;
- distinct workflow ids can proceed concurrently;
- existing frozen tests remain unchanged and green.

This finding does not authorize that repair or a new experiment.
