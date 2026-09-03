# Adversarial Verification — workflow lifecycle atomicity

**Date:** 2026-09-03  
**Level:** 1. Not Experiment 04. Not Defect C. PBT-P5 not closed.

---

| Check | Result |
|---|---|
| Branch base | `fix/lifecycle-atomicity` off `ab146f5` (Stage 1). Ancestors: `ab146f5`, `5b38c4b` |
| Frozen tests | unmodified. `tests/test_phase1_properties.py` not touched |
| PBT-P5 | still `allowed == len(paths)` and `files_changed == 0` |
| Additive | `git diff --stat master..HEAD` — no deleted files |
| Defect A red | `assert lab.tracked_workflows() <= 1` failed with `2 <= 1` (seam forced both past the first check) |
| Defect B red | `assert set(lab._states) == set(lab._locks)` failed: states `{'wf-stale'}`, locks empty |
| Defect A/B green | same tests, hooks reached, invariants hold |
| Defect A hook site | `_capacity_seam` is inside `_admit`, after the first look, before insert. Splitting `_admit` without a re-check fails `tracked_workflows() <= 1` (red: `2 <= 1`). A seam that only sat in `submit` before `_admit` stayed green on that split. |
| Suite twice | **170 passed / 0 failed** (165 prior + 5 this slice) |
| Concurrency 100x | 100/100 ok after moving the Race A seam into `_admit`; 100/100 ok on the first landing |
| Defect D | not present — `state()` still locks known ids (Block A) |
| `finish()` | documented as trusted coordinator API, not an agent action |

Red run (verbatim pytest, above the composition summary):

```text
FAILED tests/test_workflow_lifecycle_atomicity.py::test_capacity_check_and_reservation_are_atomic
FAILED tests/test_workflow_lifecycle_atomicity.py::test_finish_does_not_orphan_state_on_stale_lock_reference
```

Green run (verbatim):

```text
170 passed in 6.49s
170 passed in 6.61s
```

```text
NEXT STEP: STOP
```

No Experiment 04. No I2 verb-completeness. No I9 global default-deny.
