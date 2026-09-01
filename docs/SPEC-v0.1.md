# Agent Authority Lab — Experiment Specification v0.1

## Purpose

Agent Authority Lab is not a product and not a new IAM system. It is an experimental testbed for one hypothesis:

> Can the safe operating space of autonomous AI agents be constrained more effectively by combining Least Authority, Information Flow Control, and Stateful Invariant Enforcement than by tool/capability permissions alone?

The experiment should try to falsify the hypothesis.

## Security classes

### A — Formal Authority
Who may perform which action on which resource?

### B — Information Flow
What information may flow from which source to which destination?

### C — Composition Safety
What cumulative state changes may a sequence of individually allowed actions produce?

### D — Semantic Alignment
Does the final result truly match what the human intended?

Class D is explicitly **not** treated as a hard deterministic security guarantee.

## Trusted boundary

Untrusted: LLM, planner, agents, sub-agents, natural-language rationale, agent memory, agent output.

Trusted for the experiment: capability validation, deterministic policy enforcement, information-flow checks, workflow-state monitor, fake adapter, provenance recorder.

No security decision may depend on an LLM response.

## Fake world

All tests run locally with fake repositories, fake CI, fake network, fake GitHub, fake secrets and fake agents. No real credentials or production services are allowed.

## Data labels

Minimal labels: `PUBLIC`, `INTERNAL`, `SENSITIVE`, `SECRET`.

## Core experiment

Each action is checked against authority, information flow and predicted state transition. Unknown conditions default to deny.

The experiment compares baselines:

- A: tool permissions only
- B: capabilities / least authority
- C: capabilities + information flow
- D: capabilities + information flow + stateful invariant enforcement

## Attack families

The full test matrix includes direct forbidden action, confused deputy, information laundering, sharded exfiltration, composition attacks, verifier manipulation, slow drift, budget splitting, cross-capability composition, multi-agent collusion, encoding/transformation and allowed-channel abuse.

## Success is not assumed

A STOP result is valid if additional complexity does not create measurable protection, if false positives are too high, if policies become unmanageable, or if safety depends on LLM judgments.
