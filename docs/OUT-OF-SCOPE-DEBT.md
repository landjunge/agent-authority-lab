# Out-of-Scope Debt

OUT OF SCOPE is **visible technical debt**, not a license to ignore a security-relevant class.

Status: `OPEN` · `ACCEPTED MODEL LIMITATION` · `PLANNED` · `RESOLVED`

No row here authorizes an experiment. `PLANNED` is unused unless a future spec is explicitly frozen.

| ID | Problem | Security relevance | Why currently excluded | Could invalidate broader claim | Current evidence | Potential future experiment | Status |
|---|---|---|---|---|---|---|---|
| OOS-001 | Unmodeled raw control flow | High | Exp 03 only models `control_decide` / `created_under` | Yes — “implicit flows solved” | Exp 03 review remaining weakness | Language-level taint (not authorized) | OPEN |
| OOS-002 | Compromised trusted runtime | Critical | Trusted store is the TCB | Yes — all IFC | Exp 02 §13 | Runtime attestation (not authorized) | ACCEPTED MODEL LIMITATION |
| OOS-003 | Wrong initial labels | High | Labels minted at `customer.read` | Yes — IFC follows garbage in | Exp 02 non-claims | Source labeling study | OPEN |
| OOS-004 | Off-channel communication | High | Only workflow objects are channels | Yes — composition monitor bypass | Exp 02 | Shared-memory / side-file lab | OPEN |
| OOS-005 | Cross-session information laundering | Medium–high | No durable session model | Yes — if claim is long-horizon | Isolation is per workflow object | Persistence experiment | OPEN |
| OOS-006 | Timing channels | Medium | No time in security decision | Yes — noninterference | None | Timing lab | OPEN |
| OOS-007 | Covert channels | High | Not modeled | Yes | Exp 02/03 | Covert-channel lab | OPEN |
| OOS-008 | Arbitrary byte transformations | High | Only `copy`/`derive`/`wrap` | Yes — unmodeled mutation | Exp 01 limitation | Byte-edit API then IFC | OPEN |
| OOS-009 | Semantic composition | High | No meaning analyzer | Yes — alignment/harm | Honesty: no DLP | Explicitly refused | ACCEPTED MODEL LIMITATION |
| OOS-010 | Prompt injection | High | No LLM in lab | Yes — “agents are safe” | None | Injection eval (forbidden unless new spec) | OPEN |
| OOS-011 | Real distributed execution | High | Single-process fake | Yes — distributed IFC | None | Multi-process lab | OPEN |
| OOS-012 | Real agent frameworks | High | Custom fake APIs | Yes — framework gaps | None | Integration (not authorized) | OPEN |
| OOS-013 | Real credential brokers | High | No real credentials | Yes — secret handling | Threat model | 4AllPass/Tollgate forbidden here | ACCEPTED MODEL LIMITATION |
| OOS-014 | Real external services | High | Fake `https://external.example` | Yes — network IFC | In-memory `external` list | Real HTTP forbidden | ACCEPTED MODEL LIMITATION |
| OOS-015 | Human approval fatigue | Medium | Tokens are truthy flags | Yes — I6 as real approval | Phase 1 I6 model limit | Crypto/human study | ACCEPTED MODEL LIMITATION |
| OOS-016 | Declassification | High | No downgrade channel | Yes — if claimed | Exp 01: no declassify | Separate spec if ever authorized | OPEN |
| OOS-017 | Aggregation inference | High | Single-bit encode only | Yes — many PUBLIC bits | Exp 03 one status field | Aggregation experiment | OPEN |
| OOS-018 | Long-horizon state corruption | Medium–high | Short pytest workflows | Yes — drift over days | Slow-drift is I1 count, not months | Horizon lab | OPEN |
| OOS-019 | I2 keys on the exact string `file.write`; other mutating verbs are not counted | High | Frozen I2 / `WRITE_ACTIONS`; PBT-P5 documents the gap on purpose | Yes — `file.create` (and any unlisted write verb) bypasses the unique-file cap | PBT-P5: `allowed == len(paths)` and `files_changed == 0` | Verb-complete I2 (not authorized) | OPEN |
| OOS-020 | Approval-Token ist ein reiner Wahrheitswert; nicht an Actor, Aktion, Ressource, Workflow oder Generation gebunden (RC-03/04/05, CB-01) | High | Same core as OOS-015 (truthy flags; ACCEPTED MODEL LIMITATION) | Yes — I6 as bound capability | Real-case transfer RC-03/04/05; convergence CB-01 | Token binding (not authorized) | ACCEPTED MODEL LIMITATION |

I8/I9 historical SPEC CONFLICT remains in ADR-001 and old reviews — not “resolved away.”
