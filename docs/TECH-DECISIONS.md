# Technology Decisions — v0.1

These choices are research defaults, not permanent product commitments.

## Capability layer

**Selected for Lab v0.1: Biscuit**

Reason: compact fit for offline verification, attenuation/delegation experiments and external revocation state. UCAN remains a comparison reference.

Rule: do not invent a new token format.

## Authorization policy

**Selected for Lab v0.1: Cedar**

Reason: clean separation of principal/action/resource/context authorization with deterministic allow/deny semantics. OPA remains a comparison candidate if the lab later needs more general state-policy evaluation.

## Information flow

**Reference existing IFC work such as FIDES; do not build a new IFC system in v0.2.**

For the first prototype, information-flow behavior may be represented by a minimal deterministic test abstraction sufficient to compare baselines. The research contribution under test is the composition/state layer, not a new IFC implementation.

## Custom experimental surface

Only these pieces are intended to be custom in the first prototype:

- Workflow state
- Transition validator
- Deterministic invariant set
- Fake adapters/environment
- Attack harness
- Provenance + metrics
