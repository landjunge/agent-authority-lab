"""G3: Lab emits envelope JSONL without changing ALLOW/DENY."""

from __future__ import annotations

import json
from pathlib import Path

from lab.models import ActionRequest
from lab.validator import Lab


def test_emit_off_by_default_under_pytest(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("LAB_AUTHORITY_EVENTS", raising=False)
    monkeypatch.setenv("LAB_AUTHORITY_EVENTS_PATH", str(tmp_path / "x.jsonl"))
    Lab().submit(ActionRequest("A", "file.write", "src/app.py", {}, "wf-off"))
    assert not (tmp_path / "x.jsonl").exists()


def test_emit_allow_and_deny_jsonl(tmp_path: Path, monkeypatch) -> None:
    out = tmp_path / "authority-events.jsonl"
    monkeypatch.setenv("LAB_AUTHORITY_EVENTS", "1")
    monkeypatch.setenv("LAB_AUTHORITY_EVENTS_PATH", str(out))
    lab = Lab()
    ok = lab.submit(ActionRequest("A", "file.write", "src/app.py", {}, "wf-emit"))
    deny = lab.submit(
        ActionRequest("A", "file.write", "config/security-policy.json", {}, "wf-emit")
    )
    assert ok.allow is True
    assert deny.allow is False
    lines = [json.loads(x) for x in out.read_text(encoding="utf-8").splitlines() if x.strip()]
    assert [e["event_type"] for e in lines] == [
        "authority.requested",
        "authority.allowed",
        "authority.requested",
        "authority.denied",
    ]
    for ev in lines:
        assert ev["source_tool"] == "agent-authority-lab"
        assert ev["workflow_id"] == "wf-emit"
        assert ev["trace_id"] == "wf-emit"
        assert "api_key" not in ev
        assert "secret" not in ev
    assert lines[1]["decision"] == "ALLOW"
    assert lines[3]["decision"] == "DENY"
    assert lines[1]["previous_event_hash"] == lines[0]["event_hash"]
    assert not list(tmp_path.glob("*.sqlite"))


def test_emit_does_not_flip_deny(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("LAB_AUTHORITY_EVENTS", "1")
    monkeypatch.setenv("LAB_AUTHORITY_EVENTS_PATH", str(tmp_path / "x.jsonl"))
    d = Lab().submit(ActionRequest("A", "file.write", "config/security-policy.json", {}, "wf"))
    assert d.allow is False
