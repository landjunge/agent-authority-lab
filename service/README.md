# Agent Authority Service v0.1

A production-oriented service layer derived from the Agent Authority Lab.

The lab remains the research source of truth. This service does **not** claim general agent safety.

## Contract

Every relevant agent action is submitted to the Authority Gateway and receives exactly one decision:

- `ALLOW`
- `DENY`
- `REQUIRE_APPROVAL`

The service keeps workflow state, records provenance, binds approvals to one exact action fingerprint, emits append-only audit events, and exposes a Blind Map describing known coverage limits.

## Trust boundary

Agents must not call critical tools directly. Trusted adapters execute only an `ALLOW`ed request whose fingerprint matches the evaluated request. Lifecycle/reset operations remain coordinator-only.

## Run

```bash
python -m pytest service/tests -q
```

This v0.1 is an in-process reference service. Durable storage, authentication, multi-process coordination, cryptographic approval signatures, and tamper-evident audit persistence are intentionally not claimed yet.
