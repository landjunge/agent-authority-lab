"""Red-first probe for the confirmed finish-to-adapter-effect lifecycle gap."""

from __future__ import annotations

import threading

from lab.fake_adapter import FakeAdapter


def test_no_adapter_effect_occurs_after_finish_returns() -> None:
    adapter = FakeAdapter()
    workflow_id = "wf-finish-effect-gap"
    path = "src/late.py"
    authorized = threading.Event()
    release_effect = threading.Event()
    original_submit = adapter.lab.submit
    result = []

    def submit_then_pause(req):
        decision = original_submit(req)
        assert decision.allow is True
        authorized.set()
        assert release_effect.wait(timeout=5)
        return decision

    adapter.lab.submit = submit_then_pause  # type: ignore[method-assign]

    worker = threading.Thread(
        target=lambda: result.append(
            adapter.write("agent-a", path, workflow_id, "late effect")
        )
    )
    worker.start()
    assert authorized.wait(timeout=5)

    assert adapter.lab.finish(workflow_id) is True
    assert path not in adapter.repo.files

    release_effect.set()
    worker.join(timeout=5)
    assert not worker.is_alive()
    assert result and result[0].allow is True

    # Desired lifecycle property: once finish() returned, no effect from that
    # generation may appear later.
    assert path not in adapter.repo.files
