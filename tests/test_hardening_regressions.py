"""Regression tests for runtime-boundary hardening."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from time import sleep

import lab.validator as validator_module
from lab.fake_adapter import FakeAdapter
from lab.models import INVALID_REQUEST, ActionRequest
from lab.validator import Lab


def test_parallel_submits_cannot_bypass_action_budget(monkeypatch):
    lab = Lab()
    wid = "wf-concurrent-budget"
    lab.state(wid).action_count = 99

    original = validator_module.predict_next

    def slow_prediction(state, request):
        # Widen the old read/check/commit race window deterministically.
        sleep(0.05)
        return original(state, request)

    monkeypatch.setattr(validator_module, "predict_next", slow_prediction)
    requests = [ActionRequest(str(i), "file.read", str(i), {}, wid) for i in range(2)]

    with ThreadPoolExecutor(max_workers=2) as pool:
        decisions = list(pool.map(lab.submit, requests))

    assert [d.allow for d in decisions].count(True) == 1
    assert [d.allow for d in decisions].count(False) == 1
    assert lab.state(wid).action_count == 100
    assert len(lab.state(wid).provenance) == 1


def test_adapter_executes_against_canonical_identity():
    adapter = FakeAdapter()
    adapter.repo.files["tests/security/check.py"] = "important"

    decision = adapter.delete(
        "A", "tests/other/../security/check.py", "wf-canonical-adapter", "approved"
    )

    assert decision.allow is True
    assert "tests/security/check.py" not in adapter.repo.files


def test_malformed_request_fails_closed_without_state_creation():
    lab = Lab()
    malformed = ActionRequest("A", "repo.delete", "repo", None, "wf-invalid")  # type: ignore[arg-type]

    decision = lab.submit(malformed)

    assert decision.allow is False
    assert decision.deny_reason == INVALID_REQUEST
    assert decision.violated_invariants == [INVALID_REQUEST]
    assert "wf-invalid" not in lab._states
