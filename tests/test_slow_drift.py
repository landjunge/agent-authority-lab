"""Many individually allowed steps eventually hit a cumulative limit (I1). No intent."""

from lab.attacks import slow_drift
from lab.models import I1_ACTION_BUDGET
from lab.validator import Lab


def test_slow_drift_denies_when_cumulative_limit_reached():
    lab = Lab()
    wid = "wf-drift"
    reqs = slow_drift(wid, n=101)
    for req in reqs[:100]:
        d = lab.submit(req)
        assert d.allow is True
        assert lab.state(wid).files_changed == 0  # reads do not count as file changes
    denied = lab.submit(reqs[100])
    assert denied.allow is False
    assert denied.deny_reason == I1_ACTION_BUDGET
    assert lab.state(wid).action_count == 100
    # DENY did not append provenance
    assert len(lab.state(wid).provenance) == 100
