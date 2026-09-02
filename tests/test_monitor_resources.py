"""Resource behaviour of the monitor itself.

Two properties that are easy to lose and hard to notice:

* A reference monitor that runs out of memory is fail-crash, not fail-closed.
  The state table grows by one entry plus one lock per distinct workflow id and
  is never released, so anyone able to pick ids can grow it without limit.

* ``snapshot()`` runs on every ``submit``. If it deep-copies the provenance, the
  cost of one action grows with the history behind it, making a workflow
  quadratic in its own length.
"""

from __future__ import annotations

import time

from lab.models import CAPACITY_EXCEEDED, MAX_ACTIONS, ActionRequest
from lab.validator import Lab


def _read(lab: Lab, workflow_id: str, path: str = "src/app.py"):
    return lab.submit(ActionRequest("agent-a", "file.read", path, {}, workflow_id))


# ── lifecycle ───────────────────────────────────────────────────────────────


def test_finish_releases_state_and_lock():
    lab = Lab()
    for i in range(5):
        _read(lab, f"wf-{i}")
    assert lab.tracked_workflows() == 5

    assert lab.finish("wf-3") is True
    assert lab.tracked_workflows() == 4
    assert lab.finish("wf-3") is False, "finishing twice must be a no-op"
    assert "wf-3" not in lab._locks, "the lock outlived the workflow"


def test_finished_workflow_starts_clean_if_reused():
    lab = Lab()
    for _ in range(4):
        _read(lab, "wf-1")
    assert lab.state("wf-1").action_count == 4

    lab.finish("wf-1")
    _read(lab, "wf-1")
    assert lab.state("wf-1").action_count == 1


def test_new_workflows_are_refused_at_capacity():
    lab = Lab(max_tracked=3)
    for i in range(3):
        assert _read(lab, f"wf-{i}").allow

    overflow = _read(lab, "wf-overflow")
    assert overflow.allow is False
    assert overflow.deny_reason == CAPACITY_EXCEEDED
    assert lab.tracked_workflows() == 3


def test_capacity_does_not_block_existing_workflows():
    """The cap must not turn into a denial-of-service against live work."""
    lab = Lab(max_tracked=2)
    _read(lab, "wf-a")
    _read(lab, "wf-b")
    assert _read(lab, "wf-c").allow is False

    assert _read(lab, "wf-a").allow is True
    assert lab.state("wf-a").action_count == 2

    lab.finish("wf-b")
    assert _read(lab, "wf-c").allow is True


# ── cost ────────────────────────────────────────────────────────────────────


def test_action_cost_does_not_grow_with_history():
    """A deep-copying snapshot makes action N cost O(N). Pin the flat shape.

    The ratio is compared against the *first* action, and the bound is loose
    (5x) so this does not turn into a flaky benchmark. The bug it guards against
    produced a factor of 44 across a single 100-action workflow.
    """
    lab = Lab()
    timings = []
    for i in range(MAX_ACTIONS - 1):
        start = time.perf_counter()
        lab.submit(ActionRequest("agent-a", "file.read", f"p{i}", {}, "wf-1"))
        timings.append(time.perf_counter() - start)

    early = min(timings[:10])
    late = min(timings[-10:])
    assert late < early * 5, (
        f"cost grows with history: early={early * 1e6:.0f}us late={late * 1e6:.0f}us"
    )


def test_full_workflow_stays_fast():
    lab = Lab()
    start = time.perf_counter()
    for i in range(MAX_ACTIONS - 1):
        lab.submit(ActionRequest("agent-a", "file.read", f"p{i}", {}, "wf-1"))
    elapsed = time.perf_counter() - start
    assert elapsed < 0.5, f"a full workflow took {elapsed * 1000:.0f}ms"
