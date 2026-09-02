# ADR-002 — Research method and review semantics

**Status:** accepted  
**Date:** 2026-09-01  
**Does not amend** Phase 1 prototypes, Phase 2 experiment specs, ADR-001, or historical reviews.

## Context

The lab grew a repeated loop (freeze spec → implement → do not weaken tests → suite twice → probes → STOP) across many files. Reviews titled “Independent Verification” can be misread as third-party audits. PASS on pytest can be misread as SUPPORTED for general agent safety. OUT OF SCOPE can be misused to hide a fail. STOP can be misread as “research is over” or ignored as “keep building.”

I8/I9 showed that silent spec repair is forbidden; interpretation belongs in an ADR (`docs/ADR-001-I8-I9-action-boundary.md`). That file is unchanged.

## Decision

The research method is a **stable layer**, documented in:

- `docs/RESEARCH-METHOD.md` (protocol)
- `docs/THREAT-MODEL.md`
- `docs/OUT-OF-SCOPE-DEBT.md`
- `docs/EVALUATION-MATRIX.md`

Rules:

1. **PASS ≠ SUPPORTED.** Axis A (conformance) and Axis B (hypothesis) are independent. PASS+REFUTED and PASS+INCONCLUSIVE are valid.
2. **STOP = no automatic scope expansion.** It ends the current cycle, not the research program. A new experiment needs new authorization, question, frozen hypothesis, and spec.
3. **Historical Independent Verification files remain historical.** Titles and verdicts stay. They are interpreted as Level 1 (same-context adversarial / post-implementation verification), not Level 3/4 external audits, unless a future document records an actual external reviewer.
4. **Future internal reviews** use **Adversarial Verification** or **Post-Implementation Verification**. **Independent External Review** only if the reviewer is actually external.
5. **OUT OF SCOPE** for a security-relevant class **creates or updates a debt row**. It does not convert a spec FAIL into PASS.
6. **Experiment-result confidence** and **generalization confidence** are always separate.
7. **Methodology changes** that would reinterpret old results require a new ADR (or an explicit update to this ADR) **before** that reinterpretation is used. Old reviews are not rewritten to match the new method.

## Consequences

- README points here and must not claim production safety or that v0.2 is the whole lab.
- Experiment 04 (and I10+, declassification, prompt injection, real agents, Biscuit/Cedar/FIDES, 4AllPass) remain unauthorized until a new frozen spec exists.
- Program-level STOP (`RESEARCH-METHOD.md` §3.1) is additive: `n=10`, `k≥4` refutes generalization. It does not reinterpret historical PASS/SUPPORTED strings. The battery is not this ADR and is not authorized by it.
- Authors must not weaken old tests or frozen specs to obtain PASS.
- A finished slice is on `origin`, not only on the author’s disk. Push is part of the loop.

## Status

Accepted for all work after this ADR. Does not retroactively change historical PASS/SUPPORTED strings in old files; it changes **how those strings may be cited**.
