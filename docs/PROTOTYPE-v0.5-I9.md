# Agent Authority Lab — Prototype v0.5 (I9 only)

**Additive research slice. Does not amend `docs/PROTOTYPE-v0.2.md`, `docs/PROTOTYPE-v0.3.md`, or `docs/PROTOTYPE-v0.4.md`.**

This slice is **only I9**. It is not a product, not a global default-deny, and not semantic action classification.

v0.2–v0.4 remain frozen.

## 1. Research question

Can a deterministic **safe-set** rule on protected resource identities prevent action-name bypasses without an LLM or semantic interpretation?

v0.4 / I8 closed complementary verbs *inside* a frozen mutating-verb set (`file.write`, `file.delete`, `file.remove`, `file.rename`, `file.unlink`). The v0.4 review (`docs/REVIEW-v0.4.md`) found the next structural hole: the monitor matches **exact action strings**. Unfamiliar strings (`file.rm`, `os.remove`, `git.rm`, `File.write`, `FILE.DELETE`, `delete`, `unlink`) targeting the same protected identities were ALLOW.

## 2. Hypothesis

For a protected canonical resource identity:

- known actions proceed under existing I1–I8 rules;
- an unknown action string must not gain authority merely because it is unfamiliar.

**Unknown verb + protected object = DENY.**

The monitor does **not** interpret what the unknown verb “really means”. `os.remove` is not classified as `file.delete`. It is refused because it is not in the frozen vocabulary and the resource is protected.

This is a falsifiable experiment. A FAIL is an acceptable research result.

## 3. Protected identities (canonical, unchanged)

Use existing `canonical_path` / `is_protected_path` / `is_security_test_path`. Do not broaden the matcher.

- `config/security-policy.json`
- `tests/test_security.py`
- any path under `tests/security/`

Must remain **unprotected** (existing exclusivity set):

- `tests/test_security_notes.txt`
- `tests/test_my_security_helper.py`
- `tests/security_backup/test_a.py`
- `tests/other/security/foo.py`
- `src/test_security.py`
- `docs/security/test_policy.py`
- `security/test_policy.py`

## 4. Frozen known/safe action vocabulary

Exact strings. No case folding. No regex. No fuzzy match. No LLM. Do not grow this set to silence adversarial probes.

```text
file.read
file.write
file.delete
file.remove
file.rename
file.unlink
delegate
net.connect
repo.delete
release.publish
```

These are the actions already used by v0.2–v0.4. Their existing invariant semantics are unchanged.

## 5. I9 deterministic rule

```text
if canonical(resource) is a protected identity
   and action is not in the frozen known/safe vocabulary
then DENY with reason I9_UNKNOWN_ACTION_PROTECTED
```

Corollaries:

1. Known read / non-mutating operations on protected identities behave as before (`file.read` of the policy is not I3/I8/I9).
2. Known mutating operations remain governed by I3 / I7 / I8 and existing approval rules. I9 does not replace them.
3. `approval_token` does **not** authorize an unknown action on a protected identity.
4. I9 does **not** deny unknown actions on ordinary (non-protected) resources.

### Deny-reason precedence

Evaluate I1–I8 first, then I9. `deny_reason` is the first violated invariant.

| Request | `deny_reason` |
|---|---|
| known `file.write` of the policy | `I3_PROTECTED_PATH` (frozen) |
| known `file.delete` of a security-test artifact, no token | `I7_SECURITY_TEST_DELETE` (frozen) |
| known `file.delete` / `file.remove` / … of the policy | `I8_PROTECTED_MUTATION` (frozen) |
| known `file.write` of a security-test artifact, no token | `I8_PROTECTED_MUTATION` (frozen) |
| **unknown** action on a protected identity | `I9_UNKNOWN_ACTION_PROTECTED` |

## 6. Acceptance

- All v0.2, v0.3, and v0.4 tests remain green **without modification**.
- `file.rm` of `tests/test_security.py` → DENY I9; state unchanged.
- `os.remove` of `tests/test_security.py` → DENY I9.
- `git.rm` of `config/security-policy.json` → DENY I9; a truthy `approval_token` does not bypass.
- `File.write` of `tests/test_security.py` → DENY I9 (no silent lowercasing).
- `FILE.DELETE` of `config/security-policy.json` → DENY I9.
- `destroy` of `config/security-policy.json` → DENY I9.
- `os.remove` of `./tests/../tests/test_security.py` → DENY I9 (path canonicalization ∘ action identity).
- `custom.inspect` of `src/app.py` → I9 does **not** deny.
- `custom.inspect` of `tests/test_security_notes.txt` → I9 does **not** deny (resource not protected).
- Known `file.write` of the policy still `I3_PROTECTED_PATH`, not I9.
- `repo.nuke` of the policy with a truthy token → DENY I9.
- Every I9 DENY leaves workflow state byte-for-byte equal on the spec fields listed in the I9 gate (including `actor_depth` and provenance).

## 7. Out of scope

- Semantic / LLM / probabilistic action classification
- Growing the known set by blacklisting adversarial strings
- Global default-deny for unknown actions on ordinary resources
- Biscuit / Cedar / FIDES
- Cryptographic tokens
- I2-on-delete, adapter key canonicalization, `..` root clamp
- Real git, network, agents, secrets, 4AllPass
- v0.6 / I10

## 8. Falsification (I9 FAIL)

- An unknown action targeting a protected identity is ALLOW when no previous explicitly defined rule authorizes that exact action.
- Path aliases bypass I9.
- `approval_token` turns an unknown policy action into ALLOW.
- I9 broadens the protected resource set.
- I9 globally blocks unknown actions on ordinary resources.
- DENY mutates workflow state.
- Frozen tests must be weakened.
- An LLM or classifier is required for the security decision.

Do not repair the specification to obtain PASS.

## 9. Frozen prior slices

v0.2, v0.3, and v0.4 specifications, invariants, and acceptance tests are frozen. I9 is additive only.
