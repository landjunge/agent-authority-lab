"""Global workflow counters — per-agent budgets must not bypass I1."""

from lab.models import I1_ACTION_BUDGET, ActionRequest
from lab.validator import Lab


def test_cross_agent_accumulation_shares_one_state():
    lab = Lab()
    wid = "wf-acc"
    for i in range(100):
        actor = "A" if i < 50 else "B"
        d = lab.submit(ActionRequest(actor, "file.read", f"p/{i}", {}, wid))
        assert d.allow is True
    # B has only 50 personal actions; a per-agent cap of 100 would allow this.
    denied = lab.submit(ActionRequest("B", "file.read", "p/more", {}, wid))
    assert denied.allow is False
    assert denied.deny_reason == I1_ACTION_BUDGET
    st = lab.state(wid)
    assert st.action_count == 100
    assert st.agents == {"A", "B"}
    assert len(st.provenance) == 100


def test_separate_workflow_ids_do_not_share_budget():
    lab = Lab()
    for i in range(10):
        assert lab.submit(ActionRequest("A", "file.read", f"x/{i}", {}, "wf-1")).allow
    for i in range(10):
        assert lab.submit(ActionRequest("B", "file.read", f"y/{i}", {}, "wf-2")).allow
    assert lab.state("wf-1").action_count == 10
    assert lab.state("wf-2").action_count == 10
