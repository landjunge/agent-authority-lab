# Independent Verification — Phase 2 Experiment 02

**Frozen spec:** `docs/PHASE2-EXPERIMENT-02-COMMUNICATION-GATE.md` (`a693ac68a829b1db2899341e4f4e16427f2bd884`)  
**Implementation commit tested:** `ee443b9a54bb91d3edbf37485c4a5f636089d456`  
**Date:** 2026-09-01  
**Method:** spec freeze first; implement only `communication_gate.py` + `gated_runtime.py` + new tests; Experiment 01 and Phase 1 unmodified; `pytest -q` twice.

No implementation changes after this review. No Experiment 03.

---

## Verdict

```text
PHASE 2 EXPERIMENT 02:

BASELINE:
66 passed / 0 failed

COMMUNICATION GATE TESTS:
28 passed / 0 failed

FULL SUITE RUN 1:
94 passed / 0 failed

FULL SUITE RUN 2:
94 passed / 0 failed

DIRECT BYPASS:
BLOCKED
(no workflow_send / deliver_direct on GatedWorkflow; B holdings empty until gate+receive)

LABEL FORGERY:
BLOCKED
(request_transfer extra kwargs ignored; C1 stays SENSITIVE)

PROVENANCE FORGERY:
BLOCKED
(origin remains fake://customers)

VALUE SUBSTITUTION:
BLOCKED
(P1 payload stays hello world; C1 payload stays CUSTOMER_001; no rebind API)

CROSS-WORKFLOW SUBSTITUTION:
BLOCKED
(CROSS_WORKFLOW_REFERENCE)

REPLAY:
BLOCKED
(consumed message_id → REPLAY)

PAYLOAD CONTENT ACCESS BY GATE:
NONE

GATE WRITE AUTHORITY:
NONE
(gate does not commit inbox; runtime does after ALLOW)

GATE NETWORK AUTHORITY:
NONE

GATE CREDENTIAL ACCESS:
NONE

GATE TOOL EXECUTION:
NONE

PUBLIC COMMUNICATION:
ALLOW

SENSITIVE INTERNAL COMMUNICATION:
ALLOW

SENSITIVE EXTERNAL EGRESS:
DENY
(Experiment 01 IFC after gated receive)

PROVENANCE ACROSS AGENT BOUNDARY:
PASS
(checkpoint A→CommunicationGate→B; origin unchanged)

DENIED TRANSFER STATE INTEGRITY:
PASS

HYPOTHESIS:
SUPPORTED

WHAT THIS DEMONSTRATES:
In the Experiment 02 fake world, agents cannot deliver a value to
another agent without evaluate_transfer. The gate sees only
(workflow_id, sender, receiver, value_id) and trusted metadata.
It does not read payloads, run tools, or mint authority. Forgery,
substitution, cross-workflow, and replay fail. PUBLIC transfer and
egress still work. SENSITIVE still dies at egress.

WHAT THIS DOES NOT DEMONSTRATE:
That the whole lab is gated (Experiment 01 still has direct A→B
by design). Compromised runtime, covert/side/implicit channels,
unmodeled byte edits, collusion off-channel, cryptographic
non-replay, or general agent safety. The gate is not “no read
access at all”; it reads security metadata.

STRONGEST REMAINING WEAKNESS:
The Communication Gate is optional architecture sitting beside
Experiment 01, not a forced interceptor of every Python object.
Unmodeled channels and a compromised trusted runtime remain
out of model (as the spec listed).

CONFIDENCE:
HIGH inside Experiment 02. LOW as a statement about agents in general.

NEXT STEP:
STOP
```

---

## Privilege audit

| Capability | Gate |
|---|---|
| Read payload | NO |
| Read security metadata | YES (via `MetadataView`) |
| Read policy | YES (constant `INTERNAL_TRANSFER_ALLOWED`) |
| Modify policy / provenance / label | NO |
| Write repository / filesystem | NO |
| External network | NO |
| Agent tool execution | NO |
| Credential access | NO |
| Mint / delegate authority | NO |
| Return ALLOW/DENY | YES |
| Record security decision | YES (`decisions` log, no payload) |

`CommunicationGate` public functions: `__init__`, `evaluate_transfer`, `_record`. No `execute`, `read_payload`, `write`, `external_send`, `grant`.

If more authority had been required: STOP. It was not.

---

## Honesty

- Gate is not “block all comms”: A→B PUBLIC ALLOW, B→A PUBLIC ALLOW, multi-message ALLOW.  
- Not DLP: PUBLIC payload `CUSTOMER_001` transfers conceptually as PUBLIC and B may egress it.  
- Composition C1→D1→gate→B→D2→claimed-PUBLIC P1→egress DENY; path `[C1, D1, D2, P1]`; no payload in explanation.  
- Experiment 01 tests still 20/20; Phase 1 46/46.

---

## Failure modes (not solved)

Compromised trusted runtime; wrong initial labels; unmodeled/covert/side/implicit flows; off-channel collusion; arbitrary unmodeled transforms; metadata tampering outside the model; DoS by denying communication. Spec §13. Do not claim otherwise.
