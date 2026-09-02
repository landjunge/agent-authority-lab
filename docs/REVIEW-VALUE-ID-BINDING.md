# Adversarial Verification — Phase 2 value-id binding

**Date:** 2026-09-02  
**Level:** 1 (same-context). Not an external audit.

Not Experiment 04. Frozen Exp 01–03 specs and tests unmodified.

---

## Checks

| Check | Result |
|---|---|
| Frozen Exp 01–03 tests | unmodified, green |
| Suite twice | **139 passed / 0 failed** (132 prior + 7 this slice) |
| ChatGPT 5-step collision Exp 01 | DENY `VALUE_ID_COLLISION`; B egress DENY; `external == []` |
| In-flight overwrite Exp 02 | DENY; receive still SENSITIVE; B egress DENY |
| Exp 03 remint PUBLIC `C1` | DENY; catalog remains SENSITIVE |
| Empty `derive` | DENY `EMPTY_TRANSFORM`, no `IndexError` |
| Same-id transfer send/receive | still ALLOW |

## Axis A

**PASS** for `docs/PHASE2-VALUE-ID-BINDING.md`.

## Axis B (Exp 01–03 hypotheses)

The collision was a runtime-binding FAIL inside the modeled APIs. After this repair, the original IFC/gate claims are again consistent with the evidence **inside those APIs**. That is **PARTIALLY SUPPORTED** restored, not a new general-safety proof. Unique ids are now an enforced mint rule, not an unstated test convention.

## Residuals

- Ids are still caller-chosen strings, not cryptographic names.
- Same-binding remint (identical label/origin/payload) remains ALLOW (idempotent).
- `verify_consumer`-style identity confusion is Tollgate, not this lab.

```text
NEXT STEP: STOP
```

No Experiment 04.
