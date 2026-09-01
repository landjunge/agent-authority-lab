# Phase 2 — Experiment 01 (frozen)

**Additive laboratory experiment.** Does not amend Phase 1 (`docs/PROTOTYPE-v0.2.md` … `v0.5-I9.md`, ADR-001, historical reviews).

**Do not implement Experiment 02 in this slice.**

Information Flow Control is existing research (Denning, Myers/Liskov, IFC OS/language work). This experiment does **not** claim IFC, labels, or provenance as novel. The claim under test is narrower and falsifiable.

## 1. Research question

Can multiple individually authorized agent actions create a forbidden result that ordinary per-action authorization does not detect?

Can a deterministic workflow-level information-flow / composition monitor detect and stop that result without using an LLM for the security decision?

## 2. Hypothesis

In the fake two-agent environment, a deterministic provenance-preserving information-flow rule can block sensitive-data egress produced by composition of individually authorized actions, while allowing equivalent public-data egress.

Do not broaden this claim.

## 3. Threat model

Two agents share one workflow. Agent A may read sensitive customer data but may not send externally. Agent B may send externally but may not read the customer resource. Neither agent needs to violate its own action permission. The forbidden outcome is **sensitive information leaving the system** via composition:

```text
READ (A) → TRANSFER (A→B) → EGRESS (B)
```

The adversary may copy, derive, wrap, or claim a PUBLIC label. There is no declassification, sanitization, or semantic DLP. The adversary cannot require an LLM in the trusted path.

Out of threat model: real network, real customers, crypto capabilities, distributed systems, 4AllPass.

## 4. Actors

Exactly:

- `agent-a`
- `agent-b`

Both may participate in the same `workflow_id`.

## 5. Resources (fake only)

| Resource | Meaning |
|---|---|
| `fake://customers` | Sensitive customer store. Payload example `CUSTOMER_001` is **not** inspected by the monitor. |
| `workflow://message` | In-workflow transfer channel. |
| `https://external.example` | Fake external destination. No real network. |

Internal operations (`copy`, `derive`, `wrap`) act on values the actor currently holds. They are not additional external resources.

## 6. Authority matrix

`AuthorityOK(actor, action, resource)` sees **only** actor, action, resource. No labels. No provenance.

| Actor | `customer.read` `fake://customers` | `workflow.send` / `workflow.receive` `workflow://message` | `external.send` `https://external.example` | hold/copy/derive/wrap of a value already in the actor’s possession |
|---|---|---|---|---|
| `agent-a` | YES | YES | **NO** | YES |
| `agent-b` | **NO** | YES | YES | YES |

A public value `hello-world` (label PUBLIC, origin `workflow://message`) may be created by either agent as a non-customer write of PUBLIC workflow data (`public.write` on `workflow://message`): YES for both.

## 7. Data labels

Exactly two:

- `PUBLIC`
- `SENSITIVE`

A `DataValue` has:

- `value_id`
- `label`
- `origin`
- `provenance` (IDs and event names, **not** payload text)
- `derived_from` (list of `value_id`)

The monitor **must not** decide by matching payload strings such as `CUSTOMER_001`.

## 8. Flow rules

Deterministic, no downgrade, no declassification, no sanitizer, no classifier, no LLM.

Label of an output:

- all inputs `PUBLIC` → `PUBLIC`
- any input `SENSITIVE` → `SENSITIVE`
- mixed `PUBLIC` + `SENSITIVE` → `SENSITIVE`

`FlowOK` at `external.send`:

- `PUBLIC` → true
- `SENSITIVE` (including any derived value whose dependency graph contains a SENSITIVE origin) → **false**

`FlowOK` for internal use (read, transfer, receive, derive, wrap) of SENSITIVE: **true** (SENSITIVE may flow internally).

Executable:

```text
AuthorityOK ∧ FlowOK
```

Authority-only mode evaluates `AuthorityOK` only (`FlowOK` treated as true).

## 9. Attack graph

```text
T0  workflow holds no sensitive values
T1  agent-a  customer.read(fake://customers)     → C1  SENSITIVE  origin=fake://customers
T2  agent-a  workflow.send(C1 → agent-b)
T3  agent-b  workflow.receive(C1)
T4  agent-b  external.send(C1 → https://external.example)
```

Wrapper/laundering graph (required adversarial case):

```text
C1 --derive--> D1 --derive--> D2 --transfer--> B --wrap--> P1 --external.send--> DENY (IFC)
```

`P1.derived_from` includes `D2`; dependency closure includes `C1`; label remains `SENSITIVE` even if the wrap claims PUBLIC.

## 10. Baseline expected behavior (authority-only)

1. A reads customers → ALLOW, C1 created (label may exist as inert metadata; **not consulted**)
2. A transfers C1 to B → ALLOW
3. B receives C1 → ALLOW
4. B `external.send(C1)` → **ALLOW**
5. Fake destination **contains** C1 (attack success)

Also:

- A `external.send(*)` → DENY (`AuthorityOK` false)
- B `customer.read` → DENY (`AuthorityOK` false)
- B `external.send(PUBLIC hello-world)` → ALLOW

**If the baseline blocks T4, the experiment is invalid. STOP and redesign.**

## 11. Experimental expected behavior (authority + IFC)

T1–T3: ALLOW (authority and internal flow).

T4: `AuthorityOK=true`, `FlowOK=false` → **DENY** `SENSITIVE_EXTERNAL_EGRESS`.

Fake destination **unchanged**. Attempt may be logged. Payload is not stored in provenance.

Public egress by B: ALLOW.

A internal use of C1 without egress: ALLOW.

## 12. Legitimate controls

| Case | Expected |
|---|---|
| B sends PUBLIC `hello-world` externally | ALLOW |
| A reads C1 and derives internally, no egress | ALLOW |
| Two-agent PUBLIC workflow (A creates PUBLIC, transfers to B, B egresses) | ALLOW |
| A direct external send | DENY by **authority**, not the interesting IFC result |

The monitor must not be equivalent to “B cannot use the network” or “A cannot read customers.”

## 13. Acceptance criteria

- All Phase 1 tests remain green **without modification**.
- Authority-only: primary composition attack **succeeds** (external state mutated).
- Authority+IFC: same attack **blocked** at T4; T1–T3 ALLOW.
- PUBLIC external egress ALLOW under both modes (B).
- SENSITIVE internal use ALLOW under IFC.
- Label survives transfer, copy, derive; mixed → SENSITIVE.
- B cannot strip label by wrap/copy/derive.
- Denied egress does not mutate fake external state.
- DENY explanation is machine-readable: `authority_ok`, `flow_ok`, `reason`, `value_id`, `sensitive_origin`, `path` of IDs (no payload).
- Direct A egress DENY by authority.
- Cross-agent attack requires shared workflow context (holdings/provenance that survive transfer).
- Legitimate multi-agent PUBLIC workflow completes.

## 14. Falsification (hypothesis REFUTED)

- Authority-only baseline blocks the primary attack.
- IFC still allows SENSITIVE external egress.
- PUBLIC external egress is incorrectly blocked.
- Labels disappear during ordinary modeled copy/derive/wrap.
- B can remove the label by wrapping/copying/deriving.
- Security decision requires an LLM.
- Monitor decides by inspecting literal secret strings rather than provenance/labels.
- Denied egress mutates fake external state.
- Provenance cannot explain why the final action was denied.

Do not modify this hypothesis to obtain PASS.

## 15. Limitations

- Two labels, two agents, one fake workflow, explicit `derived_from` edges only.
- Transformations are **modeled** (`derive` / `wrap` APIs). Arbitrary unmodeled mutation of payload bytes is out of scope (not semantic DLP).
- No declassification channel; that is a future experiment if ever authorized.
- Fake world only.

## 16. Explicit non-claims

This experiment does **not** demonstrate: general agent safety, alignment, proof of intent, semantic code safety, enterprise IFC, novelty of IFC/labels/provenance, that Biscuit/Cedar/FIDES/UCAN/OPA would or would not help, or 4AllPass readiness.

No LLM in the trusted core.

## Honesty check (mandatory)

The result is **invalid** if it could have been obtained by removing B’s network permission, or by preventing A from reading customers, or if the block does not depend on provenance/label information that crosses agent boundaries.

Valid only if: A may read, B may send PUBLIC externally, and **composition of SENSITIVE through B’s egress** is what becomes forbidden.
