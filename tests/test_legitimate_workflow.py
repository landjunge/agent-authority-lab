"""Normal two-agent workflow stays ALLOW for all 30 actions / 6 files."""

from lab.models import ActionRequest
from lab.validator import Lab


def test_legitimate_workflow_fully_allowed():
    lab = Lab()
    wid = "wf-ok"
    files = [f"src/mod{i}.py" for i in range(6)]
    # 6 unique writes split across A and B
    for i, path in enumerate(files):
        actor = "A" if i % 2 == 0 else "B"
        d = lab.submit(ActionRequest(actor, "file.write", path, {}, wid))
        assert d.allow is True, d
    # 24 additional reads → 30 actions total
    for i in range(24):
        actor = "A" if i % 2 == 0 else "B"
        d = lab.submit(ActionRequest(actor, "file.read", files[i % 6], {}, wid))
        assert d.allow is True, d
    st = lab.state(wid)
    assert st.action_count == 30
    assert st.files_changed == 6
    assert st.agents == {"A", "B"}
    assert st.network_destinations == set()
    assert st.irreversible_effects == []
    assert len(st.provenance) == 30
    for rec in st.provenance:
        assert rec.decision == "ALLOW"
        assert rec.workflow_id == wid
        assert rec.state_after["action_count"] == rec.state_before["action_count"] + 1
        assert rec.timestamp.endswith("Z")
        assert "approval_token" not in rec.state_before
        assert "secret" not in str(rec)
