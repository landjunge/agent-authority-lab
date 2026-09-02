# Phase 1 repair — FakeAdapter path identity (T-19)

Additive. Does **not** rewrite v0.2–v0.5 reviews or Phase 2 specs. Not Experiment 04.

Submit atomicity and `INVALID_REQUEST` already landed (`docs/PHASE1-SUBMIT-ATOMICITY.md`). This slice only closes the FakeAdapter half of T-19: the monitor counted canonical paths while `FakeRepo` used the raw request string.

## Rule

`FakeAdapter` canonicalizes **once** at the edge. The same string is:

- `ActionRequest.resource` (monitor identity)
- the `FakeRepo` key on ALLOW write/delete

`canonical_path` is unchanged (still drops unmatched `..`; still no case fold). DENY still does not insert or pop repo keys.

## Acceptance

- `write` of `src/a.py`, `./src/a.py`, `src/foo/../a.py` → one repo key `src/a.py`, `files_changed == 1`.
- `delete` of an alias pops that same key.
- Frozen tests unmodified and green.
- P7 (adapter DENY does not mutate repo) still holds.

## Out of scope

- Rejecting `..` that leaves the root
- OS case folding
- Real filesystems / tmpdir
- A future adapter that bypasses `FakeAdapter`

## Falsification

- Frozen tests weakened
- Alias writes produce two repo keys while the monitor counts one
- DENY write/delete mutates `FakeRepo`
