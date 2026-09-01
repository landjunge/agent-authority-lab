"""v0.5 I9: unknown actions on protected identities. Frozen v0.2–v0.4 tests stay unmodified."""

from lab.fake_adapter import FakeAdapter
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
        tuple((r.seq, r.action, r.resource, r.decision) for r in st.provenance),
    )


def _deny_i9(action, resource, params=None, wid="wf-i9"):
    lab = Lab()
    before = _freeze(lab.state(wid))
    d = lab.submit(ActionRequest("A", action, resource, params or {}, wid))
    after = _freeze(lab.state(wid))
    assert d.allow is False, (action, resource, d)
    assert d.deny_reason == I9_UNKNOWN_ACTION_PROTECTED
    assert I9_UNKNOWN_ACTION_PROTECTED in d.violated_invariants
    assert after == before
    return d


def test_1_unknown_delete_alias_file_rm():
    _deny_i9("file.rm", SEC, wid="wf-i9-1")


def test_2_os_remove_on_security_test():
    _deny_i9("os.remove", SEC, wid="wf-i9-2")


def test_3_git_rm_on_policy_token_does_not_bypass():
    _deny_i9("git.rm", POLICY, params={"approval_token": "APPROVE-I9"}, wid="wf-i9-3")
    _deny_i9("git.rm", POLICY, wid="wf-i9-3b")


def test_4_case_variant_File_write_not_reinterpreted():
    _deny_i9("File.write", SEC, wid="wf-i9-4")


def test_5_uppercase_FILE_DELETE_on_policy():
    _deny_i9("FILE.DELETE", POLICY, wid="wf-i9-5")


def test_6_generic_unknown_destroy_on_policy():
    _deny_i9("destroy", POLICY, wid="wf-i9-6")


def test_7_unknown_action_plus_alias_path():
    _deny_i9("os.remove", "./tests/../tests/test_security.py", wid="wf-i9-7")


def test_8_unknown_action_on_ordinary_resource_not_i9():
    lab = Lab()
    d = lab.submit(ActionRequest("A", "custom.inspect", "src/app.py", {}, "wf-i9-8"))
    assert d.deny_reason != I9_UNKNOWN_ACTION_PROTECTED
    assert d.allow is True


def test_9_excluded_security_like_filename_not_protected():
    lab = Lab()
    d = lab.submit(
        ActionRequest("A", "custom.inspect", "tests/test_security_notes.txt", {}, "wf-i9-9")
    )
    assert d.deny_reason != I9_UNKNOWN_ACTION_PROTECTED
    assert d.allow is True


def test_10_known_policy_write_still_i3_not_i9():
    d = Lab().submit(ActionRequest("A", "file.write", POLICY, {}, "wf-i9-10"))
    assert d.allow is False
    assert d.deny_reason == I3_PROTECTED_PATH
    assert I9_UNKNOWN_ACTION_PROTECTED not in d.violated_invariants


def test_10b_known_security_delete_still_i7():
    d = Lab().submit(ActionRequest("A", "file.delete", SEC, {}, "wf-i9-10b"))
    assert d.allow is False
    assert d.deny_reason == I7_SECURITY_TEST_DELETE
    assert I9_UNKNOWN_ACTION_PROTECTED not in d.violated_invariants


def test_10c_known_policy_delete_still_i8():
    d = Lab().submit(ActionRequest("A", "file.delete", POLICY, {}, "wf-i9-10c"))
    assert d.allow is False
    assert d.deny_reason == I8_PROTECTED_MUTATION
    assert I9_UNKNOWN_ACTION_PROTECTED not in d.violated_invariants


def test_11_token_cannot_authorize_unknown_policy_action():
    _deny_i9("repo.nuke", POLICY, params={"approval_token": "APPROVE-TOKEN-XYZ"}, wid="wf-i9-11")


def test_12_deny_state_integrity_across_i9_cases():
    cases = [
        ("file.rm", SEC, {}),
        ("os.remove", SEC, {}),
        ("git.rm", POLICY, {"approval_token": "T"}),
        ("File.write", SEC, {}),
        ("FILE.DELETE", POLICY, {}),
        ("destroy", POLICY, {}),
        ("os.remove", "./tests/../tests/test_security.py", {}),
        ("repo.nuke", POLICY, {"approval_token": "T"}),
    ]
    lab = Lab()
    wid = "wf-i9-12"
    for action, resource, params in cases:
        before = _freeze(lab.state(wid))
        d = lab.submit(ActionRequest("A", action, resource, params, wid))
        after = _freeze(lab.state(wid))
        assert d.allow is False, (action, resource, d)
        assert d.deny_reason == I9_UNKNOWN_ACTION_PROTECTED
        assert after == before


def test_known_read_on_policy_still_allowed():
    d = Lab().submit(ActionRequest("A", "file.read", POLICY, {}, "wf-i9-read"))
    assert d.allow is True


def test_denied_unknown_does_not_change_fakerepo():
    ad = FakeAdapter()
    snap = dict(ad.repo.files)
    d = ad.lab.submit(ActionRequest("A", "os.remove", POLICY, {}, "wf-i9-repo"))
    assert d.allow is False
    assert d.deny_reason == I9_UNKNOWN_ACTION_PROTECTED
    assert ad.repo.files == snap
