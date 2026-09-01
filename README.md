# Agent Authority Lab

Experimental security lab for testing whether **Least Authority + Information Flow Control + Stateful Invariant Enforcement** provides measurable protection beyond action-level authorization alone.

## Status

**Specification frozen at Prototype v0.2. No production implementation yet.**

The lab is intentionally separate from 4AllPass. It uses no real credentials, no production systems, and no real secrets.

## Research question

Can a workflow of individually authorized agent actions still create a forbidden cumulative outcome, and can a small deterministic composition monitor detect those cases without putting an LLM in the trusted core?

## Rules

- Use existing security primitives where possible.
- No custom cryptography.
- No custom capability format unless a concrete gap is demonstrated.
- LLMs may propose actions but must not authorize them.
- Tests are acceptance criteria and must not be weakened to fit an implementation.
- A failed hypothesis is a valid research result.

## Frozen sequence

1. Spec v0.1
2. Composition Gate
3. Technology decisions
4. Prototype Spec v0.2
5. Build deterministic prototype
6. Test against frozen v0.2
7. GO/STOP decision before v0.3

See `docs/` for the frozen design documents.

## v0.2 prototype (deterministic core)

Local composition monitor only. No LLM, no network, no real credentials.

```text
ActionRequest → predict next WorkflowState → evaluate I1–I6
  ALLOW: commit state + provenance
  DENY:  leave state unchanged
```

### Invariants

| ID | Rule |
|---|---|
| I1 | `action_count <= 100` |
| I2 | unique written files `<= 10` |
| I3 | `config/security-policy.json` is immutable |
| I4 | `delegation_depth <= 1` |
| I5 | any `net.connect` destination is forbidden |
| I6 | `repo.delete` / `release.publish` need `parameters.approval_token` |

**Delegation convention:** root actor depth is 0. `root → A` is depth 1 (allowed). `A → B` is depth 2 (denied).

I4 only constrains the `delegate` action. Independent agents may still submit into the same `workflow_id` at depth 0 (required for the cross-agent accumulation tests). That is not a depth-chain.

### Run tests

```bash
python3.12 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest
```

### What v0.2 does **not** prove

- general agent safety
- alignment or proof of intent
- complete information-flow security
- semantic code safety
- enterprise readiness
- that Biscuit, Cedar, or FIDES would help (not integrated)

A STOP result on the research hypothesis is valid.

## v0.3 (canonical artifact identity)

Additive. Frozen v0.2 is unchanged. See `docs/PROTOTYPE-v0.3.md`.

- Path aliases (`./`, `..`, `//`) collapse before I2/I3.
- **I7:** `file.delete` of `tests/test_security.py` or anything under `tests/security/` needs `approval_token`.

## v0.4 (I8 — mutation completeness)

Additive. Frozen v0.2 and v0.3 are unchanged. See `docs/PROTOTYPE-v0.4.md`.

- Mutating verbs on the protected policy other than `file.write` are DENY (I8). I3 is not relaxed.
- Mutating verbs on security-test artifacts other than `file.delete` need `approval_token` (I8).
- I7 identity matcher is the v0.3 list only (no filename heuristic).
- Not in this slice: global default-deny, I2-on-delete, adapter key canonicalization.

## v0.5 (I9 — unknown action on protected identity)

Additive. Frozen v0.2–v0.4 are unchanged. See `docs/PROTOTYPE-v0.5-I9.md`.

- Unknown action string + protected canonical identity → DENY `I9_UNKNOWN_ACTION_PROTECTED`.
- Exact known/safe vocabulary only. No case folding, no alias interpretation, no LLM.
- I9 does not globally deny unknown actions on ordinary resources.
- `approval_token` does not authorize an unknown policy action.
