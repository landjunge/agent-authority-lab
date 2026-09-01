# Agent Authority Lab — Prototype v0.3

**Additive research slice. Does not amend `docs/PROTOTYPE-v0.2.md`.**

## One problem

Stateful structural invariants: **canonical artifact identity**.

v0.2 counted and protected path *strings*. Aliases (`./`, `..`, duplicate slashes) were distinct. This slice asks whether collapsing aliases to one artifact ID, and treating deletion of security tests as irreversible structure, adds protection without an LLM.

## In scope

1. Canonical POSIX-style path identity for I2 uniqueness and I3 protection.
2. **I7:** `file.delete` of a security-test artifact requires the same class of explicit `approval_token` as I6.

Security-test artifacts (canonical):

- `tests/test_security.py`
- any path under `tests/security/`

## Out of scope

- Biscuit / Cedar / FIDES
- Semantic “is this test weaker?”
- Relaxing I3 (protected policy stays immutable)
- Real git, network, agents, secrets

## Acceptance

- All v0.2 tests remain green without modification.
- Alias writes to the protected policy are DENY (I3).
- `./a.py` and `a.py` count as one unique file (I2).
- `file.delete` on `tests/test_security.py` without token is DENY (I7); with token ALLOW if no other invariant fires.
- Denied deletes do not mutate workflow state.
