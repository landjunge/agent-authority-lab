# ADR-001 — I8 / I9 action-boundary semantics

**Status:** accepted  
**Date:** 2026-09-01  
**Does not amend** `docs/PROTOTYPE-v0.2.md`, `v0.3.md`, `v0.4.md`, `v0.5-I9.md`, or historical reviews.

## Context

I8 (`docs/PROTOTYPE-v0.4.md`) tested a **frozen known mutating-action vocabulary**:

```text
file.write
file.delete
file.remove
file.rename
file.unlink
```

At that time, unknown action strings were **outside I8’s scope**. The v0.4 spec says the slice is “only I8” and lists under out-of-scope:

> Global default-deny for unknown actions (`repo.destroy`, `shell.exec`, `network.send`, …)

The v0.4 test `test_unknown_non_mutating_on_protected_is_out_of_scope` encoded that I8 scope boundary as **runtime ALLOW** (`assert d.allow is True` for `repo.destroy` / `shell.exec` on protected identities). Its docstring is “I8 is not global default-deny.”

I9 (`docs/PROTOTYPE-v0.5-I9.md`) later introduced a **separate** fail-closed rule: unknown action + protected canonical identity → `I9_UNKNOWN_ACTION_PROTECTED`.

Those two statements cannot both describe the **final** Decision if ALLOW means “the architecture grants permission.” Combined-suite result at `7ff1960` / `aa9f171`: **SPEC CONFLICT**.

## Decision

**Interpretation B.** The I8 ALLOW assertion was **experiment-local scope documentation**, not a permanent authorization guarantee that unknown actions on protected identities must remain allowed.

Evidence (not “make the suite green”):

1. I8 spec scope is the frozen five-verb set, not unknown verbs. Research question: whether that set on protected identities closes complementary-verb composition. Unknown action names are explicitly **out of scope**, not listed as acceptance “must ALLOW”.
2. The I8 test docstring names the property as **I8 is not global default-deny**, i.e. this layer does not classify those strings, not “the lab must authorize them.”
3. `docs/REVIEW-v0.4.md` records unknown/aliased names on protected identities as a **remaining security gap / composition gap**, and nominates I9 as the next experiment. A permanent ALLOW contract would have made I9 illegitimate; the review treated the ALLOW as **absence of a rule**.
4. Additive slices already reduced authority when an earlier slice had no rule: v0.3 made alias writes to the policy DENY (v0.2 string identity had allowed them); v0.4 made `file.write` of security tests DENY (v0.3 I7 was delete-only). I8 itself would be illegal under Interpretation A.

## Rule — monotonic security

Security invariants are **monotonic unless explicitly documented otherwise**:

- A later invariant **may reduce** authority that an earlier experiment left as final ALLOW when that ALLOW represented **absence of a rule** (layer not applicable), not an explicit required permission.
- A later invariant **may not** silently turn an earlier **explicit DENY** into ALLOW.

Terminology (documentation only; the engine remains two-state Decision allow/deny):

| Term | Meaning |
|---|---|
| **ALLOW** | final authorization result of the composition monitor |
| **NOT_APPLICABLE** | this invariant has no opinion (it does not deny) |
| **DENY** | this invariant blocks the action |

I8’s historical `allow is True` on `repo.destroy` meant **I8 is NOT_APPLICABLE**, not **ALLOW is a granted right**.

## Consequences

- I8 still owns known mutating-action behavior (`MUTATING_ACTIONS`). I8 denial reasons are unchanged.
- I9 owns unknown-action behavior at protected identity boundaries.
- I3 / I7 / I8 denial precedence remains intact; I9 does not reclassify known verbs.
- Unknown actions on ordinary (non-protected) resources remain outside I9 (not a global default-deny).
- Historical reviews (`docs/REVIEW-v0.4.md`, `docs/REVIEW-v0.5-I9.md`) remain unchanged. The conflict is documented, not erased.
- `repo.destroy` and `shell.exec` are **not** added to `KNOWN_ACTIONS`.

## Status of I9

Accepted as a legitimate additive restriction, once the I8 test asserts I8-layer NOT_APPLICABLE rather than a permanent final ALLOW.
