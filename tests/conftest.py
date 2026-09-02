from __future__ import annotations

import pytest

from lab.validator import Lab

try:
    from hypothesis import settings
except ImportError:
    pass
else:
    settings.register_profile("lab", max_examples=80, deadline=None, derandomize=True)
    settings.load_profile("lab")

ATTACK_TESTS = {
    "test_budget_splitting_denies_action_101",
    "test_file_limit_denies_eleventh_unique_file",
    "test_protected_path_write_denied",
    "test_delegation_depth_boundary",
    "test_irreversible_without_token_denied",
    "test_irreversible_with_token_allowed",
    "test_cross_agent_accumulation_shares_one_state",
    "test_slow_drift_denies_when_cumulative_limit_reached",
}
LEGIT_TESTS = {
    "test_legitimate_workflow_fully_allowed",
}


@pytest.fixture
def lab() -> Lab:
    return Lab()


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    passed = {x.nodeid.split("::")[-1] for x in terminalreporter.stats.get("passed", [])}
    failed = {x.nodeid.split("::")[-1] for x in terminalreporter.stats.get("failed", [])}
    attack_pass = len(passed & ATTACK_TESTS)
    attack_fail = len(failed & ATTACK_TESTS)
    legit_pass = len(passed & LEGIT_TESTS)
    legit_fail = len(failed & LEGIT_TESTS)
    # False positive: legitimate workflow blocked. False negative: an attack test failed
    # (monitor did not catch the frozen case).
    reporter = terminalreporter
    reporter.write_sep("=", "v0.2 composition summary")
    reporter.write_line("ATTACK TESTS")
    reporter.write_line(f"{attack_pass} passed")
    reporter.write_line(f"{attack_fail} failed")
    reporter.write_line("LEGITIMATE WORKFLOWS")
    reporter.write_line(f"{legit_pass} passed")
    reporter.write_line(f"{legit_fail} blocked")
    reporter.write_line("FALSE POSITIVES")
    reporter.write_line(f"{legit_fail}")
    reporter.write_line("FALSE NEGATIVES")
    reporter.write_line(f"{attack_fail}")
