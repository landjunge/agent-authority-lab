"""Agent A 60 + Agent B 41 in one workflow → action 101 denied (I1)."""

from lab.attacks import budget_split
from lab.models import I1_ACTION_BUDGET
from lab.validator import Lab


def test_budget_splitting_denies_action_101():
    lab = Lab()
    wid = "wf-budget"
    reqs = budget_split(wid)
    assert len(reqs) == 101
    for req in reqs[:100]:
        d = lab.submit(req)
        assert d.allow, d
    denied = lab.submit(reqs[100])
    assert denied.allow is False
    assert denied.deny_reason == I1_ACTION_BUDGET
    assert I1_ACTION_BUDGET in denied.violated_invariants
    assert lab.state(wid).action_count == 100
    record = {
        "test": "budget_splitting",
        "expected": "DENY_AT_101",
        "actual": "DENY_AT_101",
        "result": "PASS",
    }
    assert record["result"] == "PASS"
