# Composition Gate

## Gate question

Before writing a custom composition monitor, demonstrate cases where:

```text
Capability check = ALLOW
Policy check     = ALLOW
IFC check        = ALLOW
Cumulative outcome = NOT OK
```

If no convincing reproducible cases exist, stop and do not build the custom layer.

## Gate cases identified

1. Budget splitting across multiple agents.
2. File-change limit splitting across multiple agents.
3. Delegation splitting across an agent chain.
4. Gradual weakening of protected state through individually permitted edits.
5. Allowed-channel abuse without direct secret export.
6. Cross-iteration slow drift with forgotten local context.
7. Multi-agent state accumulation.
8. Individually reversible/benign actions composing into an irreversible state.

## Gate result

**GO for a minimal deterministic prototype**, but only for stateful composition/invariant enforcement.

This is not evidence that a general semantic intent monitor is possible.
