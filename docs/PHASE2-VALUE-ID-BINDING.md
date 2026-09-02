# Phase 2 repair — value-id binding

Additive. Does **not** rewrite `PHASE2-EXPERIMENT-01.md`, `02`, or `03`. Not Experiment 04. Not I10.

Frozen Exp 02 already required: the trusted runtime owns `(workflow_id, value_id)` identity; nobody may change SENSITIVE → PUBLIC; agents reference ids, they do not rewrite labels. Implementation allowed a second mint under the same id. That is a spec FAIL of the runtime binding, not a new research question.

## Hypothesis (repair)

If minting a value is refused when the id already binds a different security identity, then the ChatGPT collision (SENSITIVE `C1` overwritten as PUBLIC `C1`, then B egress) is DENY in Experiment 01, 02, and 03. Empty `derive` is DENY, not a crash.

## Rule

A **mint** is `customer.read`, `public.write`, `copy`, `derive`, `wrap`, `control.decide`, `state.write` (new payload identity).

| Existing catalog/envelope for `value_id` | Incoming mint | Decision |
|---|---|---|
| none | any | ALLOW (first binding) |
| same `label`, `origin`, `derived_from`, payload | provenance-only / extra holder | ALLOW |
| any security field differs (including SENSITIVE → PUBLIC) | | DENY `VALUE_ID_COLLISION`; store unchanged |

**Transfer** (`workflow.send` / `receive`, gate `request_transfer` / `receive`) is not a mint. It may append provenance on the existing identity. It must not change `label`, `origin`, `derived_from`, or payload.

`message_id` remains the one-time delivery token (Exp 02). It is not a second value identity.

`derive` / `copy` / `wrap` with no inputs: DENY `EMPTY_TRANSFORM`. No `IndexError`.

FlowOK still walks dependencies, but **the held object’s own label/origin is taint**, even if a later catalog row were to diverge.

## Acceptance

- Frozen Exp 01–03 tests unmodified and green.
- After A `customer.read(C1)` (SENSITIVE) and transfer to B, A `public.write(C1)` is DENY `VALUE_ID_COLLISION`. Catalog/envelope still SENSITIVE. B `external.send(C1)` still DENY under IFC.
- Same collision DENY in Experiment 02 if A overwrites after gate transfer and before B receive. In-flight `message_id` still names SENSITIVE `C1`.
- Experiment 03: minting PUBLIC `C1` after SENSITIVE `C1` is DENY; catalog unchanged.
- `derive(actor, "D0", [])` DENY `EMPTY_TRANSFORM` in all three runtimes.
- DENY does not commit catalog, envelope, holdings, inbox, `external`, or workflow_state.

## Out of scope

- Experiment 04, I10, real agents, cryptographic ids
- Changing I9 / WRITE_ACTIONS
- Versioned ids as an alternative to DENY (not this slice)

## Falsification

- Frozen tests weakened
- SENSITIVE `C1` then PUBLIC `C1` ALLOW and B egress ALLOW under IFC
- Empty derive raises
- Transfer of the same C1 (send/receive) DENY solely because the id already exists
