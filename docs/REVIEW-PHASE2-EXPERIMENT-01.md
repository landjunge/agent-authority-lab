# Independent Verification — Phase 2 Experiment 01

**Implementation commit tested:** `25e80edb5048f0da3d2483a3ed93bb80c7e6ab44`  
**Frozen spec:** `docs/PHASE2-EXPERIMENT-01.md` (`a742272bc5104c93aed36ed26d6211df4d4aa26d`)  
**Date:** 2026-09-01  
**Method:** spec freeze first; authority-only then IFC in `lab/phase2/` only; Phase 1 files unmodified except a README pointer; `pytest -q` twice; independent A/B and honesty probes outside the assertion list.

No implementation changes after this review.

---

## Verdict

```text
PHASE 2 EXPERIMENT 01:

BASELINE AUTHORITY-ONLY:
ATTACK SUCCESS

AUTHORITY + IFC:
ATTACK BLOCKED

PUBLIC EGRESS:
ALLOW

SENSITIVE INTERNAL:
ALLOW

MULTI-HOP LABEL PROPAGATION:
PASS

WRAPPER LAUNDERING ATTACK:
BLOCKED

CROSS-AGENT PROVENANCE:
PASS

DENIED SIDE-EFFECT INTEGRITY:
PASS

PHASE 1 REGRESSION:
46 passed / 0 failed
(v0.2 summary still 8 attack / 1 legit)

PHASE 2 TESTS:
20 passed / 0 failed

FULL SUITE (both runs):
66 passed / 0 failed

HYPOTHESIS:
SUPPORTED

WHAT THIS DEMONSTRATES:
In this fake two-agent lab, per-action AuthorityOK allows
READ(A) → TRANSFER(A→B) → EGRESS(B) of SENSITIVE data.
The same workflow, with provenance-preserving labels and
FlowOK at egress, denies that send (authority_ok=true,
flow_ok=false) while B’s PUBLIC external send remains ALLOW.
The block depends on the data object’s label/derived_from
graph, not on forbidding B’s network or A’s read, and not
on matching the payload string CUSTOMER_001.

WHAT THIS DOES NOT DEMONSTRATE:
General agent safety, semantic DLP, implicit flows, arbitrary
unmodeled byte edits, declassification policy, distributed IFC,
novelty of labels/provenance/IFC, or any production system.

PRIOR-ART RELATION:
Classical information-flow control (e.g. lattice/label models).
This lab only tests whether pairing that idea with an explicit
multi-agent workflow object beats authority-only checks on one
frozen composition. No novelty claim.

NEW ATTACKS FOUND:
Unmodeled channels remain: a future API that mutated payload
bytes without calling derive/wrap would not be labeled. That is
a stated spec limitation (explicit derived_from), not a silent
false negative inside the modeled API.

FALSE POSITIVES:
None on required controls. PUBLIC hello-world egress ALLOW.
PUBLIC payload equal to CUSTOMER_001 ALLOW (no string DLP).

FALSE NEGATIVES:
None inside modeled copy/derive/wrap/transfer.
B wrap-claimed-PUBLIC still SENSITIVE and DENY at egress.

CONFIDENCE:
HIGH for the frozen fake experiment.
LOW for any generalization beyond it.

NEXT STEP:
STOP
```

---

## Honesty check

| Could the IFC result be obtained by… | Answer |
|---|---|
| Removing B’s network permission? | **No.** `agent-b` `external.send` of PUBLIC `H1` ALLOW. |
| Preventing A from reading customers? | **No.** `agent-a` `customer.read` ALLOW under IFC. |
| A special “A must not talk to B” rule? | **No.** Transfer and receive of C1 ALLOW; only egress of SENSITIVE is denied. |
| Inspecting payload `CUSTOMER_001`? | **No.** PUBLIC value with that payload egresses; DENY explanations contain IDs/origins only. |
| Does the block need provenance that crossed agents? | **Yes.** B’s AuthorityOK for external send is true; FlowOK is false because the held object’s dependency closure includes `fake://customers`. A second workflow that never received C1 cannot send it. |

Experiment design is **valid** against the spec’s honesty gate.

---

## A/B

Authority-only (`ifc=False`): T1–T4 ALLOW, `external == ["C1"]`.

Authority+IFC (`ifc=True`): T1–T3 ALLOW; T4 DENY `SENSITIVE_EXTERNAL_EGRESS`; `external == []`. Explanation:

```text
authority_ok=true flow_ok=false value_id=C1
sensitive_origin=fake://customers path=[C1]
```

Laundering: C1→D1→D2→(transfer)→wrap P1 claimed PUBLIC → DENY, path `[C1, D1, D2, P1]`.

A direct egress: DENY `AUTHORITY_DENIED` (not the interesting result).

---

## Phase 1

`git diff` of `lab/invariants.py`, `lab/models.py`, `lab/paths.py`, `lab/validator.py`, `lab/fake_adapter.py`, and Phase 1 tests vs `da171af`: empty except README pointer.

Do not start Experiment 02. Do not add Biscuit/Cedar/FIDES/real network.
