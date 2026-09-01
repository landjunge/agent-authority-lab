"""Layering: I3/I7/I8/I9 precedence and monotonic restriction. No new product rules."""

from lab.models import (
    I3_PROTECTED_PATH,
    I7_SECURITY_TEST_DELETE,
    I8_PROTECTED_MUTATION,
    I9_UNKNOWN_ACTION_PROTECTED,
    ActionRequest,
)
from lab.validator import Lab

POLICY = "config/security-policy.json"
SEC = "tests/test_security.py"


def test_deterministic_precedence():
    lab = Lab()
    d_i3 = lab.submit(ActionRequest("A", "file.write", POLICY, {}, "prec"))
    assert d_i3.allow is False and d_i3.deny_reason == I3_PROTECTED_PATH

    d_i7 = lab.submit(ActionRequest("A", "file.delete", SEC, {}, "prec"))
    assert d_i7.allow is False and d_i7.deny_reason == I7_SECURITY_TEST_DELETE

    d_i8 = lab.submit(ActionRequest("A", "file.delete", POLICY, {}, "prec"))
    assert d_i8.allow is False and d_i8.deny_reason == I8_PROTECTED_MUTATION

    d_i9 = lab.submit(ActionRequest("A", "file.rm", SEC, {}, "prec"))
    assert d_i9.allow is False and d_i9.deny_reason == I9_UNKNOWN_ACTION_PROTECTED

    d_ord = lab.submit(ActionRequest("A", "custom.inspect", "src/app.py", {}, "prec"))
    assert d_ord.deny_reason != I9_UNKNOWN_ACTION_PROTECTED
    assert d_ord.allow is True


def test_monotonic_later_layer_may_restrict_absence_of_rule():
    """v0.4 I8 did not handle unknown verbs; v0.5 I9 may DENY them. Final DENY is allowed."""
    d = Lab().submit(ActionRequest("A", "repo.destroy", SEC, {}, "mono"))
    assert d.allow is False
    assert d.deny_reason == I9_UNKNOWN_ACTION_PROTECTED
    assert I8_PROTECTED_MUTATION not in d.violated_invariants


def test_monotonic_later_layer_must_not_relax_explicit_deny():
    """An earlier explicit DENY must remain DENY. I9 must not convert I3/I7/I8 to ALLOW."""
    d3 = Lab().submit(ActionRequest("A", "file.write", POLICY, {}, "mono-deny"))
    assert d3.allow is False
    assert d3.deny_reason == I3_PROTECTED_PATH

    d7 = Lab().submit(ActionRequest("A", "file.delete", SEC, {}, "mono-deny"))
    assert d7.allow is False
    assert d7.deny_reason == I7_SECURITY_TEST_DELETE

    d8 = Lab().submit(ActionRequest("A", "file.remove", POLICY, {}, "mono-deny"))
    assert d8.allow is False
    assert d8.deny_reason == I8_PROTECTED_MUTATION
