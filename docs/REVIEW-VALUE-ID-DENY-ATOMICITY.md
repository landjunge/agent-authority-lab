# Adversarial Verification — DENY must not write `decisions`

**Date:** 2026-09-02  
**Level:** 1. Follow-up to `docs/REVIEW-VALUE-ID-BINDING.md` (that PASS missed this).

Not Experiment 04. Frozen Exp 01–03 tests unmodified.

---

ChatGPT reproduced on `ad383ae`: `control_decide` wrote `self.decisions` before `_commit_hold` denied a collision. `state_write(created_under="X")` then used the PUBLIC catalog row. B egress ALLOW.

| Check | Result |
|---|---|
| Suite twice | **145 passed / 0 failed** |
| Denied `control_decide("X")` | `decisions` unchanged; no `X` in decisions |
| `state_write(created_under="X")` after that DENY | DENY; no state row; no external |
| Identical remint after gate transfer | CommunicationGate checkpoint still in provenance |

```text
NEXT STEP: STOP
```
