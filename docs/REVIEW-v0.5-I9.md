# Independent Verification Review — Prototype v0.5 (I9)

**Role:** independent security tester after implementation  
**Implementation commit tested:** `7ff1960e68945b800667e6f95df29c5189c3fbd3`  
**Parent:** `344bc767cc3d4345061ff73ea45e40074981388f` (v0.4 review)  
**I9 spec:** `docs/PROTOTYPE-v0.5-I9.md`  
**Date:** 2026-09-01  
**Method:** baseline on `344bc76` (27 passed); I9 tests written and observed FAIL (unknown actions ALLOW); smallest allowlist rule implemented; I9 tests green; full suite twice; independent probes. Frozen v0.2–v0.4 specs and tests **not modified**.

---

## Verdict

```text
I9 VERDICT:
SPEC CONFLICT

BASELINE:
27 passed
0 failed

FINAL EXISTING + I9 TESTS:
42 passed
1 failed

ADVERSARIAL PROBES:
68 passed
0 failed

FROZEN SPECS/TESTS MODIFIED:
NO

STATE INTEGRITY:
PASS
(on all I9 DENY probes; full snapshot equality)

PROVENANCE:
PASS
(I9 DENY appends no record; known ALLOW still records; tokens not copied)

LEGITIMATE WORKFLOW:
PASS
(2 agents / 30 actions / 6 files ALLOW)

I9 HYPOTHESIS:
INCONCLUSIVE
I9 matches its own spec in isolation (16/16 I9 tests, 68/68 adversarial).
It cannot be accepted as a combined-suite PASS without changing a frozen I8 test.

NEW SECURITY GAPS FOUND:
none beyond the documented SPEC CONFLICT
leftovers unchanged and still out of scope: I2 write-only, adapter raw keys,
truthy tokens, tokened known file.write of security tests, unmatched ".."

FALSE POSITIVES:
none of the v0.3 exclusivity set
custom.inspect on src/app.py ALLOW
custom.inspect on tests/test_security_notes.txt ALLOW
unknown actions on ordinary resources ALLOW (not a global default-deny)

FALSE NEGATIVES:
none on the I9 probe list for protected identities
(file.rm, file.RM, File.write, FILE.WRITE, os.remove, os.unlink, git.rm,
 delete, remove, unlink, destroy, repo.destroy, shell.exec, custom.action,
 empty string, whitespace — all DENY I9 on policy, security-test, and alias)

RESEARCH INTERPRETATION:
I9’s fail-closed allowlist does eliminate the I8 leftover action-name bypass
on protected identities, without LLM or semantic verb classification.
A frozen I8 test encoded that leftover as a positive ALLOW assertion
(test_unknown_non_mutating_on_protected_is_out_of_scope: repo.destroy /
shell.exec on protected identities must ALLOW). I9 denies exactly those
requests. Per the I9 gate, the I8 test was not modified.

CONFIDENCE:
HIGH

NEXT STEP:
STOP
```

No I10. No repair of the I8 test. No broadening of `KNOWN_ACTIONS` to silence the conflict.

---

## 1. Freeze and baseline

```text
pre-I9 HEAD  344bc767cc3d4345061ff73ea45e40074981388f
I9 impl HEAD 7ff1960e68945b800667e6f95df29c5189c3fbd3
```

Baseline `pytest -q` on `344bc76`: **27 passed, 0 failed**.

`git diff` of frozen v0.2/v0.3/v0.4 specs and their acceptance tests vs `344bc76`: **empty**.  
`tests/test_i8_protected_mutation.py` was **not edited**.

---

## 2. TDD

I9 tests collected against pre-implementation code: **10 failed** because unknown actions returned `Decision(allow=True)`.  
Frozen-behavior assertions inside the I9 file (I3/I7/I8 precedence, ordinary-resource unknown ALLOW, notes filename not protected, `file.read` of policy ALLOW) already passed.

After implementation: I9 file **16 passed**.

---

## 3. Smallest implementation

`KNOWN_ACTIONS` is the exact v0.2–v0.4 vocabulary (10 strings). No case folding.

```text
if action not in KNOWN_ACTIONS
   and resource is protected identity
then I9_UNKNOWN_ACTION_PROTECTED
```

Evaluated **after** I1–I8 so known `file.write` of the policy remains `I3_PROTECTED_PATH`.

`approval_token` is not consulted by I9.

---

## 4. Combined suite

Both full-suite runs:

```text
42 passed, 1 failed
FAILED tests/test_i8_protected_mutation.py::test_unknown_non_mutating_on_protected_is_out_of_scope
```

v0.2 composition summary still **8 attack / 1 legit**. All v0.2, v0.3, and remaining v0.4 tests green.

The failing test (unmodified):

```python
d = Lab().submit(ActionRequest("A", "repo.destroy", SEC_TEST, {}, "wf-i8-unk"))
assert d.allow is True
d2 = Lab().submit(ActionRequest("A", "shell.exec", POLICY, {}, "wf-i8-unk2"))
assert d2.allow is True
```

Observed under I9: both DENY `I9_UNKNOWN_ACTION_PROTECTED`.

That assertion was I8’s *out-of-scope* documentation (“I8 is not global default-deny”), written as a **positive ALLOW** on protected identities. I9 is scoped default-deny on those identities, not a global default-deny (`custom.inspect` / `repo.destroy` on `src/app.py` remain ALLOW).

**Gate rule applied:** if an old test must be modified to make I9 work → **STOP**, **SPEC CONFLICT**, do not modify the test.

---

## 5. Adversarial probes (independent)

16 unknown/variant action strings × {policy, security-test, alias, ordinary} plus known-action / token / legit checks.

- Protected + unknown → I9 DENY, state unchanged.
- Ordinary + unknown → ALLOW (not I9).
- Known `file.write` policy → I3, not I9.
- Known `file.delete` security-test → I7, not I9.
- `os.remove` + token on policy → still I9.
- Known `file.read` of policy → ALLOW.
- Legitimate workflow → ALLOW.

**68 PASS, 0 FAIL** on the assertion-classified probes.

---

## 6. Why this is SPEC CONFLICT, not I9 FAIL

I9 falsification list is about I9’s own rule (unknown+protected ALLOW, alias bypass, token bypass, broadened resource set, global deny, state mutation, weakened frozen tests, LLM).

- I9’s own tests: pass.
- Adversarial I9 probes: pass.
- I9 does not globally deny.
- I9 does not broaden the resource matcher.
- Frozen tests were not weakened (they were not changed). One frozen I8 test now **fails** because it required the pre-I9 hole to remain.

The collision is between two frozen documents:

| Document | Statement |
|---|---|
| I8 test (frozen v0.4) | `repo.destroy` / `shell.exec` on protected identities **ALLOW** |
| I9 spec (this slice) | unknown action on protected identity **DENY I9** |

Resolving it would mean either (a) changing the I8 test to assert `deny_reason != I8_PROTECTED_MUTATION` instead of `allow is True`, or (b) abandoning I9. Neither was authorized.

---

## 7. STOP

Do not implement I10.  
Do not edit the I8 test in this review.  
Do not add `repo.destroy` to `KNOWN_ACTIONS` to paint the suite green.

A later explicit GO may re-scope that single I8 assertion as I8-local (I8 does not deny unknown verbs) rather than a forever ALLOW contract. That decision is outside this experiment.
