"""v0.4 I8: mutating verbs on protected identities. Frozen v0.2/v0.3 tests stay unmodified."""

from lab.fake_adapter import FakeAdapter
from lab.models import (
    I3_PROTECTED_PATH,
    I7_SECURITY_TEST_DELETE,
    I8_PROTECTED_MUTATION,
    MUTATING_ACTIONS,
    ActionRequest,
)
from lab.paths import is_security_test_path
from lab.validator import Lab

POLICY = "config/security-policy.json"
SEC_TEST = "tests/test_security.py"
SEC_DIR = "tests/security/test_policy.py"


def _freeze(st):
    return (
        st.workflow_id,
        st.action_count,
        st.files_changed,
        frozenset(st.touched_paths),
        frozenset(st.agents),
        st.delegation_depth,
        frozenset(st.network_destinations),
        tuple(st.irreversible_effects),
        tuple(sorted(st.actor_depth.items())),
        len(st.provenance),
        tuple(r.seq for r in st.provenance),
    )


def test_security_test_write_without_token_denied():
    lab = Lab()
    wid = "wf-i8-w"
    for path in (SEC_TEST, SEC_DIR, "./tests/test_security.py", "tests/x/../test_security.py"):
        before = _freeze(lab.state(wid))
        d = lab.submit(ActionRequest("A", "file.write", path, {}, wid))
        assert d.allow is False, path
        assert d.deny_reason == I8_PROTECTED_MUTATION
        assert _freeze(lab.state(wid)) == before


def test_security_test_write_with_token_allowed():
    lab = Lab()
    d = lab.submit(
        ActionRequest(
            "A",
            "file.write",
            SEC_TEST,
            {"approval_token": "APPROVE-I8"},
            "wf-i8-w-ok",
        )
    )
    assert d.allow is True
    rec = lab.state("wf-i8-w-ok").provenance[-1]
    assert rec.action == "file.write"
    assert "APPROVE-I8" not in str(rec)


def test_policy_delete_denied_even_with_token():
    lab = Lab()
    wid = "wf-i8-pol"
    for params in ({}, {"approval_token": "APPROVE-I8"}):
        before = _freeze(lab.state(wid))
        d = lab.submit(ActionRequest("A", "file.delete", POLICY, params, wid))
        assert d.allow is False, params
        assert d.deny_reason == I8_PROTECTED_MUTATION
        assert _freeze(lab.state(wid)) == before


def test_policy_write_still_i3():
    d = Lab().submit(ActionRequest("A", "file.write", POLICY, {}, "wf-i8-i3"))
    assert d.allow is False
    assert d.deny_reason == I3_PROTECTED_PATH


def test_security_delete_still_i7():
    d = Lab().submit(ActionRequest("A", "file.delete", SEC_TEST, {}, "wf-i8-i7"))
    assert d.allow is False
    assert d.deny_reason == I7_SECURITY_TEST_DELETE


def test_other_mutating_verbs_on_protected_identities():
    extra = ("file.remove", "file.rename", "file.unlink")
    lab = Lab()
    wid = "wf-i8-verbs"
    for action in extra:
        for path in (POLICY, SEC_TEST, "./config/security-policy.json"):
            before = _freeze(lab.state(wid))
            d = lab.submit(ActionRequest("A", action, path, {}, wid))
            assert d.allow is False, (action, path)
            assert d.deny_reason == I8_PROTECTED_MUTATION
            assert _freeze(lab.state(wid)) == before
        d_ok = lab.submit(
            ActionRequest("A", action, SEC_TEST, {"approval_token": "T"}, "wf-i8-verbs-tok")
        )
        assert d_ok.allow is True, action


def test_mutating_set_is_frozen():
    assert MUTATING_ACTIONS == frozenset(
        {"file.write", "file.delete", "file.remove", "file.rename", "file.unlink"}
    )


def test_denied_mutation_does_not_change_fakerepo():
    ad = FakeAdapter()
    ad.repo.files[SEC_TEST] = "ORIGINAL"
    policy = ad.repo.files[POLICY]
    snap = dict(ad.repo.files)
    d_w = ad.write("A", SEC_TEST, "wf-i8-repo", "WEAKENED")
    assert d_w.allow is False
    assert d_w.deny_reason == I8_PROTECTED_MUTATION
    assert ad.repo.files[SEC_TEST] == "ORIGINAL"
    d_d = ad.delete("A", POLICY, "wf-i8-repo")
    assert d_d.allow is False
    assert d_d.deny_reason == I8_PROTECTED_MUTATION
    assert ad.repo.files[POLICY] == policy
    assert ad.repo.files == snap


def test_legitimate_non_protected_delete_allowed():
    ad = FakeAdapter()
    ad.repo.files["src/normal.py"] = "x"
    d = ad.delete("A", "src/normal.py", "wf-i8-legit")
    assert d.allow is True
    assert "src/normal.py" not in ad.repo.files


def test_i7_matcher_is_exact_spec_set():
    assert is_security_test_path("tests/test_security.py") is True
    assert is_security_test_path("./tests/test_security.py") is True
    assert is_security_test_path("tests/security/test_policy.py") is True
    assert is_security_test_path("tests/security/nested/x.py") is True
    assert is_security_test_path("tests/test_security_notes.txt") is False
    assert is_security_test_path("tests/test_my_security_helper.py") is False
    assert is_security_test_path("tests/security_backup/test_a.py") is False
    assert is_security_test_path("tests/other/security/foo.py") is False
    assert is_security_test_path("src/test_security.py") is False
    assert is_security_test_path("docs/security/test_policy.py") is False
    assert is_security_test_path("security/test_policy.py") is False


def test_false_positive_paths_are_not_i8_or_i7():
    lab = Lab()
    wid = "wf-i8-fp"
    for path in (
        "tests/test_security_notes.txt",
        "tests/test_my_security_helper.py",
        "tests/security_backup/test_a.py",
        "src/test_security.py",
    ):
        d_del = lab.submit(ActionRequest("A", "file.delete", path, {}, wid))
        assert d_del.allow is True, path
        d_w = lab.submit(ActionRequest("A", "file.write", path, {}, wid + "-w"))
        assert d_w.allow is True, path


def test_unknown_non_mutating_on_protected_is_out_of_scope():
    """I8 is not global default-deny."""
    d = Lab().submit(ActionRequest("A", "repo.destroy", SEC_TEST, {}, "wf-i8-unk"))
    assert d.allow is True
    d2 = Lab().submit(ActionRequest("A", "shell.exec", POLICY, {}, "wf-i8-unk2"))
    assert d2.allow is True
