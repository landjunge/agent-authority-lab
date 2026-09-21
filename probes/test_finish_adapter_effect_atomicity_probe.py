"""Red-first probe for the confirmed finish-to-adapter-effect lifecycle gap.

Not part of the acceptance suite (`testpaths = ["tests"]`). Repro:

    pytest probes/test_finish_adapter_effect_atomicity_probe.py
"""

from __future__ import annotations

import threading

from lab.fake_adapter import FakeAdapter

HOOK_TIMEOUT = 5.0
JOIN_TIMEOUT = 10.0


def test_no_adapter_effect_occurs_after_finish_returns() -> None:
    adapter = FakeAdapter()
    workflow_id = "wf-finish-effect-gap"
    path = "src/late.py"
    authorized = threading.Event()
    release_effect = threading.Event()
    original_submit = adapter.lab.submit
    result = []
    errors: list[BaseException] = []

    def submit_then_pause(req):
        decision = original_submit(req)
        assert decision.allow is True
        authorized.set()
        assert release_effect.wait(timeout=HOOK_TIMEOUT)
        return decision

    adapter.lab.submit = submit_then_pause  # type: ignore[method-assign]

    def go() -> None:
        try:
            result.append(adapter.write("agent-a", path, workflow_id, "late effect"))
        except BaseException as exc:  # noqa: BLE001 — surface in parent thread
            errors.append(exc)

    worker = threading.Thread(target=go, name="finish-effect-write")
    worker.start()
    assert authorized.wait(timeout=HOOK_TIMEOUT)

    assert adapter.lab.finish(workflow_id) is True
    assert path not in adapter.repo.files

    release_effect.set()
    worker.join(timeout=JOIN_TIMEOUT)
    assert not worker.is_alive(), f"{worker.name} hung"
    assert errors == []
    assert result and result[0].allow is True

    # Desired lifecycle property: once finish() returned, no effect from that
    # generation may appear later.
    assert path not in adapter.repo.files
