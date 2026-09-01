# Evaluation Matrix

What this lab **actually runs**, and what those runs do **not** mean.

| Method | Currently used? | What it demonstrates | What it does NOT demonstrate | Evidence / location | Future value |
|---|---|---|---|---|---|
| Frozen acceptance tests | YES | Spec’d cases on this commit | General safety; unlisted attacks | `tests/`, each `PROTOTYPE` / `PHASE2-EXPERIMENT-*.md` | Keep as contract |
| Regression tests | YES | Older slices still green | That old specs were optimal | Phase 1 + Exp 01/02 files left unmodified | Required every slice |
| Repeated deterministic pytest | YES | Suite is deterministic here | Fuzzing; flaky-test hunt at scale | Reviews: two identical `pytest -q` | Reproducibility check only |
| Adversarial hand-written probes | YES | Extra attacks the author thought of | Completeness; external creativity | `/tmp` probes in reviews; some extra tests in Exp 03 | Level 1 verification |
| A/B baseline | YES | New mechanism vs authority-only or explicit-IFC-only | That baseline is the only alternative | Exp 01 `ifc=`; Exp 03 `control_deps=` | Keep |
| Honesty gates | YES | Result not from stripping required permissions / DLP / LLM | That the hypothesis is true in the world | Each Phase 2 review table | Mandatory |
| State-integrity checks | YES | DENY does not commit monitor/external state | Adapter identity (Phase 1 gap) | Phase 1 DENY snapshots; Exp 01–03 `external == []` | Keep |
| Provenance checks | YES | DENY explanations are IDs/origins, no payload | Tamper-evident logs (T-30) | Exp 01–03 explanation dicts | Keep |
| Property-based testing | **NOT USED** | — | — | — | Could stress path canonicalization |
| Fuzzing | **NOT USED** | — | — | — | Action-string / path fuzz |
| Mutation testing | **NOT USED** | — | — | — | Whether tests catch invariant deletion |
| Random test ordering | **NOT USED** | Plugin not installed; reviews documented that | Hidden order coupling | Gate review 192e452 | Optional later |
| Model checking | **NOT USED** | — | — | — | Small IFC state machine |
| Static analysis | **NOT USED** | — | — | — | Import/LLM/network guards |
| External human review | **NOT USED** | — | — | Historical “Independent Verification” is **not** this | Level 3 |
| External AI review | **NOT USED** as a separate system | — | — | Same-context model family possible | Level 3 if actually separate |
| Adversarial agent | **NOT USED** | — | — | — | Level 4 |
| Prompt-injection evaluation | **NOT USED** | — | — | OOS-010 | Only with new spec |
| Real framework integration | **NOT USED** | — | — | OOS-012 | Forbidden unless authorized |
| Real distributed execution | **NOT USED** | — | — | OOS-011 | Same |

`pytest` twice ≠ fuzzing. Green suite ≠ SUPPORTED for a broader claim.
