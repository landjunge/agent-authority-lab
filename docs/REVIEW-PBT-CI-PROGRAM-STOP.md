# Adversarial Verification — Program-STOP, PBT oracles, CI

**Date:** 2026-09-02  
**Level:** 1 (same-context adversarial / post-implementation verification). Not an external audit.

Not Experiment 04. Not I10. I9 ordinary-resource ALLOW for unknown verbs is unchanged.

---

## Checks

| Check | Result |
|---|---|
| Frozen oracles | `docs/PBT-ORACLE-v1.md` |
| Program-STOP numbers written before any attack list | `n=10`, `k≥4` in `RESEARCH-METHOD.md` §3.1 |
| Convergence battery run | **NO** (unauthorized) |
| I9 P5 inverted | **NO** |
| Frozen v0.2–v0.5 / Phase 2 acceptance tests edited | **NO** |
| Suite twice | **132 passed / 0 failed** twice (118 prior + 14 this slice) |

## Axis A (this slice)

| Item | Result |
|---|---|
| P1 `submit` does not raise | PASS |
| P2 DENY does not mutate spec fields | PASS |
| P3 `predict_next` purity | PASS |
| P4 unknown + protected → I9 | PASS |
| P5 unknown + ordinary is not I9 | PASS (ALLOW remains legal) |
| P6 unknown actor → `UNKNOWN_ACTOR`, no `KeyError` | PASS after fail-closed patch |
| P7 adapter DENY does not mutate repo | PASS |
| CI workflow present | `.github/workflows/test.yml` (Python 3.12, suite twice) |
| History squash | Not done; freeze/feat/review commits kept |

P6 was red on the unpatched monitors (`workflow_send` to `agent-evil`, `external_send("agent-x")` → `KeyError`). Fail-closed DENY is an implementation fix, not a new invariant.

## Axis B

Not scored. This slice does not claim the composition monitor generalizes.

## What PBT did *not* find (by oracle design)

`file.create` × 30 on ordinary paths remains ALLOW with `files_changed=0`. That is I2 write-only leftover, excluded from P1–P7. Encoding it as a FAIL would have inverted P5 / I9.

T-19 (adapter raw key vs canonical identity) is still excluded.

## Residuals

- GitHub branch protection / no-force-push ruleset may need a human click if the API lacks permission.
- `k`/`n` are written; the ten attacks are not.
- No mechanical lock against editing old tests beyond CI failing after the fact.

```text
NEXT STEP: STOP
```

No Experiment 04. No I10. No tmpdir filesystem in this motion.
