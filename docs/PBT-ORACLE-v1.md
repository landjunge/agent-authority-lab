# Property oracles v1

Additive tooling spec. Does **not** amend v0.2–v0.5, I8/I9, Phase 2 experiment specs, ADR-001, or ADR-002.

This is **not** Experiment 04 and **not** I10. It does not change I9’s ordinary-resource ALLOW for unknown verbs.

## Hypothesis (tooling, not a research claim)

A small set of **monitor-contract** properties, checked by Hypothesis over action/path/actor alphabets, will catch fail-open crashes and DENY-state leaks that handwritten scenarios miss.

Axis B for the composition-monitor research question is **not** scored here.

## Oracles (frozen)

A generated example **fails** this slice if any of the following is false.

| ID | Oracle | Scope |
|---|---|---|
| P1 | `Lab.submit` returns a `Decision` and does not raise | Phase 1 |
| P2 | When `Decision.allow` is false, workflow spec fields are byte-for-byte unchanged (`workflow_id`, `action_count`, `files_changed`, `touched_paths`, `agents`, `delegation_depth`, `network_destinations`, `irreversible_effects`, `actor_depth`, provenance length and `(seq, action, resource, decision)` tuples) | Phase 1 |
| P3 | `predict_next(state, req)` does not mutate `state` | Phase 1 |
| P4 | Unknown action + protected canonical identity → DENY with `I9_UNKNOWN_ACTION_PROTECTED` in `violated_invariants` (known verbs still use I3/I7/I8 precedence; this oracle only binds unknown strings) | Phase 1 I9 |
| P5 | Unknown action + ordinary (non-protected, non-security-test) resource does **not** deny with `I9_UNKNOWN_ACTION_PROTECTED`. Final ALLOW is permitted. This oracle **forbids** treating I9 as global default-deny. | Phase 1 I9 |
| P6 | Phase 2 public APIs (`Experiment`, `ImplicitFlowExperiment`, `GatedWorkflow`) never raise `KeyError` / `TypeError` / `AttributeError` on unknown actor strings. Unknown actor → `allow is False` and reason `UNKNOWN_ACTOR`. | Phase 2 |
| P7 | `FakeAdapter.write` / `delete`: DENY does not insert or pop repo keys | Phase 1 adapter |

## Explicitly not oracles

Do **not** encode these as properties in this slice. A Hypothesis example that exhibits them is **not** a FAIL of P1–P7.

- Unknown verbs on ordinary paths are DENY (would falsify I9 / P5).
- I2 counts `file.create` / `file.delete` / any verb other than exact `file.write` (documented leftover: I2 write-only).
- `canonical_path` rejects `..` that leaves the root (documented unmatched `..`).
- Case-folded protected paths are DENY (no OS case folding).
- Phase 1 DENY writes a provenance row.
- `Lab.state()` returns an immutable snapshot.
- Adapter repo key equals canonical monitor identity (T-19).

Those remain debt or later specs. Property tests here are for **contracts the current specs already require**, plus fail-closed unknown actors (P6), which no frozen spec required to crash.

## Alphabet (bounded)

Hypothesis draws from finite alphabets, not unconstrained Unicode. That is discovery inside a closed vocabulary, not a fuzzer for the universe of strings.

- Phase 1 actions: `KNOWN_ACTIONS` plus a frozen unknown set `{file.create, file.rm, os.remove, fs.write, custom.inspect, shell.exec, File.write, FILE.DELETE}`.
- Paths: ordinary `src/` files, policy aliases, security-test identities, case variants, `..` traversals.
- Phase 2 actors: `{agent-a, agent-b}` plus unknowns `{agent-evil, agent-x, AGENT-A, ""}`.

## Falsification of this slice

- Existing v0.2–v0.5 or Phase 2 acceptance tests are weakened.
- P5 is dropped or inverted so unknown ordinary actions must DENY.
- I10 or global default-deny is introduced to silence PBT examples.
- Experiment 04 is started in this motion.
- T-19 is “fixed” by making the property require the bug.

## Out of scope

- Convergence battery (see Research Method §3.1)
- Real filesystem / tmpdir
- Expanding `WRITE_ACTIONS`
- Mutation testing, model checking
