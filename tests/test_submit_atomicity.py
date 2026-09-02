"""In-process Lab.submit is serialized per workflow_id. docs/PHASE1-SUBMIT-ATOMICITY.md."""

from __future__ import annotations

import threading

from lab.models import I1_ACTION_BUDGET, ActionRequest
from lab.validator import Lab


def test_parallel_last_budget_slot_is_not_double_granted():
    lab = Lab()
    wid = "wf-race"
    for _ in range(99):
        d = lab.submit(ActionRequest("A", "file.write", "src/a.py", {}, wid))
        assert d.allow, d
    assert lab.state(wid).action_count == 99

    barrier = threading.Barrier(2)
    results: list = []

    def go(path: str) -> None:
        barrier.wait()
        results.append(lab.submit(ActionRequest("A", "file.write", path, {}, wid)))

    t1 = threading.Thread(target=go, args=("src/ra.py",))
    t2 = threading.Thread(target=go, args=("src/rb.py",))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    allows = [d for d in results if d.allow]
    denys = [d for d in results if not d.allow]
    assert len(allows) == 1, results
    assert len(denys) == 1
    assert denys[0].deny_reason == I1_ACTION_BUDGET
    st = lab.state(wid)
    assert st.action_count == 100
    assert len(st.provenance) == 100
    assert st.provenance[-1].seq == 100
