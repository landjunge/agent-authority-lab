# Independent Verification — I8 ↔ I9 conflict resolution

**Resolution commit tested:** `60bfbf7fa01f25d52f908827cd96b57299adf310`  
**I9 implementation (unchanged):** `7ff1960e68945b800667e6f95df29c5189c3fbd3`  
**Prior I9 review (unchanged):** `aa9f1715b6fa35309cf7a0402701812c14f2573a`  
**Date:** 2026-09-01  

This review does not erase `docs/REVIEW-v0.5-I9.md` (SPEC CONFLICT). It records the architectural decision that followed.

---

## Verdict

```text
CONFLICT DECISION:
INTERPRETATION B

ADR CREATED:
YES
docs/ADR-001-I8-I9-action-boundary.md

I8 TEST CHANGED:
YES
(reclassified from final ALLOW to I8-layer NOT_APPLICABLE; not deleted)

SECURITY AUTHORITY:
REDUCED
(I9 still denies unknown+protected; that restriction is accepted as additive)

FULL SUITE RUN 1:
46 passed / 0 failed

FULL SUITE RUN 2:
46 passed / 0 failed

I9 ADVERSARIAL:
68 passed / 0 failed

STATE INTEGRITY:
PASS

PROVENANCE:
PASS

LEGITIMATE WORKFLOW:
PASS

I9 FINAL STATUS:
ACCEPTED

CONFIDENCE:
HIGH

NEXT STEP:
STOP
```

---

## Evidence

Interpretation A (permanent ALLOW contract) is **not** supported.

| Source | What it actually says |
|---|---|
| `docs/PROTOTYPE-v0.4.md` | Slice is **only I8**. Frozen verb set is five names. Out of scope: “Global default-deny for unknown actions (`repo.destroy`, `shell.exec`, `network.send`, …)”. Acceptance never requires those strings to ALLOW. |
| I8 test docstring at `2003cca` | “I8 is not global default-deny.” Layer scope, not a grant of permission. |
| `docs/REVIEW-v0.4.md` | Unknown/aliased names on protected identities are a **remaining security gap**. Next-experiment candidate: I9 fail-closed on protected identities. |
| Lab history | v0.3 DENY of alias policy writes, and v0.4 DENY of security-test `file.write`, already reduced earlier final ALLOW that was only “no rule yet”. I8 itself would be illegal under Interpretation A. |

Interpretation B (experiment-local I8 boundary) **is** supported: historical ALLOW meant **I8 does not deny**, not **the architecture must authorize**.

`docs/PROTOTYPE-v0.5-I9.md` acceptance bullet “v0.4 tests remain green without modification” was the I9 **build gate**, correctly producing SPEC CONFLICT at `aa9f171`. This resolution is a separate, authorized reclassification of that one assertion’s *meaning*. Prototype specs and historical reviews were **not** rewritten to pretend there was never a conflict.

---

## What changed / what did not

Changed:

- ADR-001
- `test_unknown_non_mutating_on_protected_is_out_of_scope` → `test_unknown_actions_are_outside_i8_vocabulary`: asserts `deny_reason != I8` and that a DENY, if any, is I9
- `tests/test_architecture_layering.py`: precedence I3 → I7 → I8 → I9; monotonic restrict vs must-not-relax

Unchanged:

- `lab/` I9 implementation and `KNOWN_ACTIONS`
- `docs/PROTOTYPE-v0.2.md` … `v0.5-I9.md`
- `docs/REVIEW-v0.3.md`, `v0.4.md`, `v0.5-I9.md`
- I8 denial of known mutating verbs; I3 not relaxed

`repo.destroy` / `shell.exec` were **not** added to `KNOWN_ACTIONS`.

---

## Independent checks after resolution

1. Historical documents still in git.  
2. Conflict documented (ADR + this review + preserved SPEC CONFLICT review).  
3. I8 security not weakened (known mutations still I3/I7/I8).  
4. I9 still DENY on the full unknown-action probe list for policy, security-test, and aliases; state unchanged on DENY.  
5. Ordinary resources: unknown actions not I9.  
6. Token does not authorize unknown policy action.  
7. Known `file.write` policy → I3; known security-test `file.delete` → I7; known other protected mutation → I8.  
8. Legitimate 30/6/2 workflow ALLOW.  
9. No LLM in authorization.

---

## Architectural lesson

**ALLOW** (final Decision) and **NOT_APPLICABLE** (this layer has no opinion) must not be the same assertion.

A test that wants to freeze “this slice does not handle X” must assert `deny_reason != <this layer>`, not `allow is True`.

Later additive invariants may turn historical final ALLOW into DENY when that ALLOW was absence of a rule. They must not turn an earlier explicit DENY into ALLOW.

---

## New security gaps

None introduced. Unchanged leftovers (out of scope): I2 write-only, adapter raw keys, truthy tokens, tokened known `file.write` of security tests, unmatched `..`.

**STOP. No I10.**
