"""state() and finish() on unknown ids must not allocate. Stage 1 lifecycle."""

from lab.validator import Lab


def test_state_on_unknown_id_does_not_allocate_or_bypass_capacity():
    lab = Lab(max_tracked=1)
    lab.state("a")
    lab.state("b")
    assert lab.tracked_workflows() == 0
    assert len(lab._locks) == 0


def test_finish_unknown_does_not_call_lock_for():
    """finish() currently mints a lock then pops it, so a registry before/after
    check is already green. Count _lock_for calls so the defect is visible.
    """
    lab = Lab()
    calls: list[str] = []
    real = lab._lock_for

    def wrapped(workflow_id: str):
        calls.append(workflow_id)
        return real(workflow_id)

    lab._lock_for = wrapped  # type: ignore[method-assign]
    assert lab.finish("never-seen") is False
    assert calls == []
    assert lab.tracked_workflows() == 0
    assert len(lab._locks) == 0
