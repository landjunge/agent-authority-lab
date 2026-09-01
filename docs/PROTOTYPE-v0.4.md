# Agent Authority Lab — Prototype v0.4 (I8 only)

**Additive research slice. Does not amend `docs/PROTOTYPE-v0.2.md` or `docs/PROTOTYPE-v0.3.md`.**

This slice is **only I8**. It is not a general expansion (no global default-deny, no I2-on-delete, no adapter identity rewrite, no cryptographic tokens).

## One problem

Protected canonical identities are **verb-incomplete**.

- I3 gates `file.write` of `config/security-policy.json`.
- I7 gates `file.delete` of security-test artifacts.

Complementary mutating verbs on the same identities were individually ALLOW while I1–I7 held. v0.3 review (`docs/REVIEW-v0.3.md`) recorded that as the strongest composition gap.

Question: does applying the same structural identity set to a frozen mutating-verb set close that gap without an LLM?

## In scope

**I8 — mutation completeness for protected canonical identities.**

Protected identities (canonical, unchanged from v0.2/v0.3):

- `config/security-policy.json`
- `tests/test_security.py`
- any path under `tests/security/`

Frozen mutating verbs for this experiment:

```text
file.write
file.delete
file.remove
file.rename
file.unlink
```

Rules:

1. **Policy (I3 not relaxed).** Any mutating verb on `config/security-policy.json` is DENY. No `approval_token` override. Frozen I3 still reports `file.write`. I8 reports the other verbs.
2. **Security-test artifacts.** Any mutating verb other than `file.delete` without `approval_token` is DENY (I8). Frozen I7 still reports `file.delete` without token. With token, those verbs ALLOW if no other invariant fires.
3. **I7 matcher alignment.** Security-test identity is exactly the v0.3 list above. No filename heuristic. No “any ancestor named security”.

Canonical aliases (`./`, `..`, `//`, backslash) collapse before the check (v0.3 `canonical_path`).

## Out of scope

- Biscuit / Cedar / FIDES
- Semantic “is this test weaker?”
- Relaxing I3
- Global default-deny for unknown actions (`repo.destroy`, `shell.exec`, `network.send`, …)
- Counting `file.delete` toward I2
- FakeAdapter raw-vs-canonical store keys
- Cryptographic `approval_token` validation
- Logical-root clamp for unmatched `..`
- Real git, network, agents, secrets

## Deny reasons (preserve frozen tests)

| Case | `deny_reason` |
|---|---|
| `file.write` of the policy | `I3_PROTECTED_PATH` (frozen) |
| `file.delete` of a security-test artifact, no token | `I7_SECURITY_TEST_DELETE` (frozen) |
| other mutating verb on the policy | `I8_PROTECTED_MUTATION` |
| other mutating verb on a security-test artifact, no token | `I8_PROTECTED_MUTATION` |

## Acceptance

- All v0.2 and v0.3 tests remain green **without modification**.
- `file.write` of `tests/test_security.py` without token is DENY (I8).
- `file.write` of `tests/test_security.py` with token is ALLOW if no other invariant fires.
- `file.delete` of `config/security-policy.json` is DENY (I8), including with a token.
- Alias mutating verbs on those identities follow the same identity (`./tests/test_security.py`, `./config/security-policy.json`, …).
- `file.remove` / `file.rename` / `file.unlink` of a protected identity without (security-test) token is DENY (I8).
- Denied mutations do not change workflow state or FakeRepo contents.
- Legitimate `file.delete` of a non-protected file remains ALLOW.
- `tests/test_security_notes.txt` and `tests/test_my_security_helper.py` are **not** security-test artifacts.
