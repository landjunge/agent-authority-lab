"""Property-based tests for the Phase 1 monitor.

The existing suite is example-based: each test fixes one scenario and freezes
it. That catches regressions well and finds new gaps badly, because it can only
check the cases someone already thought of.

These tests state a *rule* and let Hypothesis look for a counterexample. Each
property below is written so that it fails on a class of bugs, not on one input.

Note on PBT-P5: it currently documents an open gap rather than asserting a fix.
See the module docstring at that test.
"""

from __future__ import annotations

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from lab.fake_adapter import FakeAdapter
from lab.models import MAX_UNIQUE_FILES, ActionRequest
from lab.paths import canonical_path
from lab.validator import Lab

SETTINGS = settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])

# Short, alias-prone path segments: "." and ".." matter more than long names.
SEGMENT = st.text("abAB._-", min_size=1, max_size=4)
PATHS = st.lists(SEGMENT, min_size=1, max_size=4).map("/".join)

# Includes near-misses of the real verbs on purpose.
VERBS = st.sampled_from(
    [
        "file.write",
        "file.read",
        "file.delete",
        "file.create",
        "fs.write",
        "FILE.WRITE",
        "net.connect",
        "agent.delegate",
    ]
)


@SETTINGS
@given(PATHS)
def test_canonical_path_is_idempotent(path: str) -> None:
    """PBT-P1: canonicalising twice equals canonicalising once.

    If this ever fails, the path identity used by I3/I8/I9 depends on how many
    times a value happened to be normalised on the way in.
    """
    once = canonical_path(path)
    assert canonical_path(once) == once


@SETTINGS
@given(PATHS)
def test_aliases_get_identical_decisions(path: str) -> None:
    """PBT-P2: two spellings of one path cannot get different verdicts."""
    alias = "./" + path
    if canonical_path(path) != canonical_path(alias):
        return
    direct = Lab().submit(ActionRequest("agent-a", "file.write", path, {}, "w"))
    aliased = Lab().submit(ActionRequest("agent-a", "file.write", alias, {}, "w"))
    assert direct.allow == aliased.allow
    assert direct.deny_reason == aliased.deny_reason


@SETTINGS
@given(st.lists(PATHS, min_size=1, max_size=12))
def test_monitor_count_matches_the_repo(paths: list[str]) -> None:
    """PBT-P3: what the monitor counts is what the repo actually holds. T-19."""
    adapter = FakeAdapter()
    baseline = set(adapter.repo.files)
    for path in paths:
        adapter.write("agent-a", path, "w", "x")

    counted = adapter.lab.state("w").files_changed
    actual = len(set(adapter.repo.files) - baseline)
    assert counted == actual


@SETTINGS
@given(st.lists(st.tuples(VERBS, PATHS), min_size=1, max_size=25))
def test_denied_actions_leave_no_trace(ops: list[tuple[str, str]]) -> None:
    """PBT-P4: a DENY changes nothing — no count, no path, no provenance row.

    This is the property the whole predict-then-commit design exists for.
    """
    lab = Lab()
    for verb, path in ops:
        before = lab.state("w")
        decision = lab.submit(ActionRequest("agent-a", verb, path, {}, "w"))
        after = lab.state("w")
        if decision.allow:
            continue
        assert before.action_count == after.action_count
        assert before.files_changed == after.files_changed
        assert before.touched_paths == after.touched_paths
        assert len(before.provenance) == len(after.provenance)


@SETTINGS
@given(st.lists(PATHS, min_size=12, max_size=40))
def test_write_verbs_other_than_file_write_are_counted(paths: list[str]) -> None:
    """PBT-P5: OPEN GAP — I2 is keyed to the literal string ``file.write``.

    ``WRITE_ACTIONS`` is ``frozenset({"file.write"})``, and I9 only fails closed
    for unknown verbs at protected paths. Any other mutating verb an adapter
    might expose — ``file.create``, ``fs.write`` — is admitted at ordinary paths
    and never reaches ``touched_paths``, so the unique-file cap does not apply
    to it at all.

    This test asserts the gap so it is visible and counted, rather than absent.
    Invert the assertion once I9 covers the whole action space; that inversion
    is the acceptance criterion for the fix.
    """
    lab = Lab()
    allowed = sum(
        1
        for path in paths
        if lab.submit(ActionRequest("agent-a", "file.create", path, {}, "w")).allow
    )

    assert allowed == len(paths)
    assert lab.state("w").files_changed == 0
    assert len(paths) > MAX_UNIQUE_FILES


@SETTINGS
@given(st.lists(st.tuples(VERBS, PATHS), min_size=1, max_size=40))
def test_repo_never_exceeds_the_file_cap(ops: list[tuple[str, str]]) -> None:
    """PBT-P6: I2 holds against the real effect surface, not just the counter."""
    adapter = FakeAdapter()
    baseline = set(adapter.repo.files)
    for verb, path in ops:
        if verb == "file.write":
            adapter.write("agent-a", path, "w", "x")
        elif verb == "file.delete":
            adapter.delete("agent-a", path, "w")

    touched = set(adapter.repo.files) ^ baseline
    assert len(touched) <= MAX_UNIQUE_FILES


@SETTINGS
@given(st.lists(st.tuples(VERBS, PATHS), min_size=1, max_size=30))
def test_provenance_rows_are_immutable(ops: list[tuple[str, str]]) -> None:
    """PBT-P7: an audit row a caller has seen can never be edited afterwards."""
    lab = Lab()
    for verb, path in ops:
        lab.submit(ActionRequest("agent-a", verb, path, {}, "w"))

    snapshot = lab.state("w")
    if not snapshot.provenance:
        return

    row = snapshot.provenance[0]
    try:
        row.state_after["files_changed"] = 999  # type: ignore[index]
        raise AssertionError("provenance row accepted a mutation")
    except TypeError:
        pass

    snapshot.provenance.clear()
    assert lab.state("w").provenance, "clearing a snapshot emptied the live log"
