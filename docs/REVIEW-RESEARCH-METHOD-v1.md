# Adversarial Verification — Research Method v1

**Method commit:** `bea9d2139d458f799f0e1f2bf9f01e5d788ae38a`  
**Baseline (pre-method):** `f2dcf8ef0407e26751cf3bf633d53d63081c8f4f`  
**Date:** 2026-09-01  
**Level:** 1 (same-context adversarial / post-implementation verification). Not an external audit.

No `lab/` or `tests/` edits. No Experiment 04. Historical Independent Verification files were not renamed.

---

## Checks

| Check | Result |
|---|---|
| HEAD before docs | `f2dcf8e` — 118/118 twice (matches Experiment 03 review) |
| After method commit | 118/118 twice; unexpected regression: none |
| `git diff f2dcf8e bea9d21 -- lab tests` | empty |
| Historical specs / ADR-001 / Phase 2 experiment specs / old reviews | unchanged |
| New files | RESEARCH-METHOD, THREAT-MODEL, OUT-OF-SCOPE-DEBT, EVALUATION-MATRIX, ADR-002 |
| README | Status updated; v0.2 freeze sentence no longer implies the whole lab is v0.2; no production-safety claim |

## Methodology self-check

1. Can PASS be misread as SUPPORTED? Mitigated: two axes, README line, legal PASS+REFUTED. Residual: old reviews still say “Independent Verification” + SUPPORTED in one block — historical, not rewritten. **Accept residual; do not rewrite history.**
2. Can OUT OF SCOPE hide a fail? Counter-rule: spec FAIL stays FAIL; security-relevant OOS must be debt. **OK.**
3. Is STOP unambiguous? Cycle end vs program end; new experiment needs new spec. **OK.**
4. Is “independent” overused for non-external review? Future naming constrained; historical titles kept. **OK.**
5. Fake vs real claims? Narrow claim + non-claims + PARTIALLY TESTED default. **OK.**
6. Reproducibility vs fuzzing? Evaluation matrix **NOT USED** for fuzz/PBT/mutation. **OK.**
7. Threats that break a broader thesis? T-15, T-18, T-21, OOS-001–018 visible. **OK.**
8. Historical conflicts visible? ADR-001 untouched; I8/I9 called out. **OK.**
9. Can a future AI rewrite tests to fit? Test-freeze + honesty gate. Enforcement is social/process, not a CI lock. **Documented limitation.**
10. SPEC CONFLICT process? STOP, ADR/resolution, no silent spec edit. **OK.**
11. REFUTED vs FAIL? Separate axes. **OK.**
12. Confidence vs generalization? Required pair. **OK.**
13. Usable without chat history? Protocol is in-repo. **OK.**

## Residual method gaps (not FAIL of this slice)

- No mechanical lock preventing someone from editing old tests.
- Level 2–4 reviews are defined, not performed here.
- Threat matrix is conservative and incomplete for the real world by design.

---

```text
RESEARCH METHOD V1:

CURRENT HEAD VERIFIED:
YES
(f2dcf8e then bea9d21; 118/118 both times)

BASELINE TEST SUITE:
118 passed / 0 failed

LAB CODE CHANGED:
NO

TESTS CHANGED:
NO

HISTORICAL SPECS CHANGED:
NO

HISTORICAL REVIEWS CHANGED:
NO

PASS VS HYPOTHESIS STATUS SEPARATED:
YES

STOP SEMANTICS DEFINED:
YES

REVIEW INDEPENDENCE LEVELS DEFINED:
YES

OUT-OF-SCOPE DEBT REGISTER:
PRESENT

THREAT MODEL:
PRESENT

EVALUATION MATRIX:
PRESENT

CONFIDENCE VS GENERALIZATION:
SEPARATED

CLAIM BOUNDARIES:
CLEAR

METHODOLOGY SELF-CHECK:
PASS

SECURITY METHOD GAPS:
No CI enforcement of test-freeze; Level 3/4 review not run;
unmodeled implicit flow (T-15) still OPEN debt.

MODEL LIMITATIONS:
Fake runtime; truthy tokens; no real agents/network/credentials;
pytest-twice is not fuzzing.

DOCUMENTATION CONFLICTS:
None in new files. Historical “Independent Verification” titles
remain and are explicitly reinterpreted, not rewritten.

CONFIDENCE:
HIGH for “docs-only method slice did not break the suite”
MEDIUM that a future author will follow STOP without social pressure
LOW for treating this as an external methodology audit

NEXT STEP:
STOP
```
