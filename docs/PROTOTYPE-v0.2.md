# Agent Authority Lab — Prototype Specification v0.2

**Frozen acceptance specification. Do not silently change this document to make an implementation pass.**

## Goal

Build a local deterministic testbed that measures whether workflow-state + transition checks + invariants provide additional security beyond action-level controls.

No real AI, no real secrets, no external services and no production integration are required in v0.2.

## Intended repository structure

```text
agent-authority-lab/
├── README.md
├── pyproject.toml
├── lab/
│   ├── models.py
│   ├── state.py
│   ├── validator.py
│   ├── invariants.py
│   ├── provenance.py
│   ├── fake_repo.py
│   ├── fake_adapter.py
│   └── attacks.py
├── fixtures/
│   └── fake_repo/
└── tests/
    ├── test_budget_split.py
    ├── test_file_limit.py
    ├── test_protected_paths.py
    ├── test_delegation_depth.py
    ├── test_irreversible_gate.py
    ├── test_cross_agent_accumulation.py
    ├── test_slow_drift.py
    └── test_legitimate_workflow.py
```

## Core models

`WorkflowState`
- workflow_id
- action_count
- files_changed
- touched_paths
- agents
- delegation_depth
- network_destinations
- irreversible_effects
- provenance

`ActionRequest`
- actor
- action
- resource
- parameters
- workflow_id

`Decision`
- allow
- deny_reason
- violated_invariants

## Six deterministic invariants

- I1: `action_count <= 100`
- I2: `unique_files_changed <= 10`
- I3: protected paths are immutable
- I4: `delegation_depth <= 1`
- I5: external network destinations are forbidden
- I6: irreversible actions require an explicit approval token

No semantic invariant such as “security tests must not be weakened” is part of v0.2.

## Validation algorithm

```text
ActionRequest
   ↓
predict next WorkflowState
   ↓
evaluate all invariants
   ↓
ALLOW or DENY + exact reason
   ↓
on ALLOW only:
commit state transition
write provenance record
```

The validator must not mutate state on denied requests.

## Required tests

### 1. Budget splitting
Agent A performs 60 actions and Agent B performs 41 more in the same workflow. Action 101 must be denied.

### 2. File limit splitting
Multiple agents collectively attempt to modify 11 distinct files. The 11th unique file modification must be denied.

### 3. Protected path
Any write to `config/security-policy.json` must be denied.

### 4. Delegation depth
With maximum depth 1, the allowed/denied boundary must be encoded unambiguously and tested. The implementation must document whether root→A is depth 0 or 1; whichever convention is selected must preserve the invariant that one further unauthorized delegation step is rejected.

### 5. Irreversible action
Fake actions such as `repo.delete` or `release.publish` without the required approval token must be denied.

### 6. Cross-agent accumulation
Agents must share one global workflow state. Per-agent counters must not bypass workflow limits.

### 7. Slow drift simulation
Many individually allowed actions across multiple steps must eventually be denied when a deterministic cumulative limit is reached. No semantic intent judgment is part of this test.

### 8. Legitimate workflow
A normal workflow with six file changes, 30 actions, two agents, no protected path modification, no forbidden network destination and no unapproved irreversible operation must complete successfully.

## Machine-readable result shape

```json
{
  "test": "budget_splitting",
  "expected": "DENY_AT_101",
  "actual": "DENY_AT_101",
  "result": "PASS"
}
```

## GO criteria for v0.3

- All deterministic attack tests pass.
- Legitimate workflow remains allowed.
- No security decision depends on an LLM.
- Denied requests do not alter workflow state.
- Provenance is produced for all committed actions and does not contain fake secret content.

## Explicitly out of scope for v0.2

- Real Biscuit integration
- Real Cedar integration
- FIDES integration
- GitHub API
- Real agents / LLM execution
- Real secrets
- Semantic code analysis
- 4AllPass integration

These are considered only after the deterministic composition core passes the frozen acceptance tests.
