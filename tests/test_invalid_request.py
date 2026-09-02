"""Malformed ActionRequest is DENY, not an exception. docs/PHASE1-SUBMIT-ATOMICITY.md."""

from lab.models import INVALID_REQUEST, ActionRequest
from lab.validator import Lab


def test_none_parameters_on_irreversible_is_invalid_request_not_crash():
    lab = Lab()
    wid = "wf-bad-params"
    d = lab.submit(ActionRequest("A", "repo.delete", "repo.delete", None, wid))  # type: ignore[arg-type]
    assert d.allow is False
    assert d.deny_reason == INVALID_REQUEST
    assert wid not in lab._states


def test_empty_actor_is_invalid_request():
    d = Lab().submit(ActionRequest("", "file.write", "src/a.py", {}, "wf-empty-actor"))
    assert d.allow is False
    assert d.deny_reason == INVALID_REQUEST


def test_overlong_resource_is_invalid_request():
    d = Lab().submit(ActionRequest("A", "file.write", "x" * 257, {}, "wf-long"))
    assert d.allow is False
    assert d.deny_reason == INVALID_REQUEST
