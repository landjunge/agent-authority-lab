"""Monitor-off oracles for the frozen catalog. Do not score monitor-on here."""

from tests.convergence.catalog import (
    cb01_steps,
    cb02_steps,
    cb03_steps,
    run_cb04_off,
    run_cb05_off,
    run_cb06_off,
    run_cb07_off,
    run_cb08_off,
    run_cb09_off,
    run_cb10_off,
)
from tests.convergence.harness import phase1_off


def test_cb01_token_reuse_monitor_off():
    st = phase1_off(cb01_steps())["cb-01"]
    assert st.irreversible_effects == ["repo.delete", "release.publish"]


def test_cb02_mixed_verb_budget_monitor_off():
    steps = cb02_steps()
    assert len(steps) == 101
    st = phase1_off(steps)["cb-02"]
    assert st.action_count == 101
    assert st.files_changed == 8
    assert st.agents == {"A", "B"}


def test_cb03_self_delegation_monitor_off():
    st = phase1_off(cb03_steps())["cb-03"]
    assert st.delegation_depth == 2
    assert st.actor_depth["root"] == 2


def test_cb04_two_secret_join_monitor_off():
    exp, d = run_cb04_off()
    assert d.allow is True
    assert "M1" in exp.external


def test_cb05_wrap_before_transfer_monitor_off():
    exp, d = run_cb05_off()
    assert d.allow is True
    assert "P1" in exp.external


def test_cb06_receiver_mix_monitor_off():
    exp, d = run_cb06_off()
    assert d.allow is True
    assert "D1" in exp.external


def test_cb07_round_trip_monitor_off():
    exp, d = run_cb07_off()
    assert d.allow is True
    assert "P1" in exp.external


def test_cb08_control_dep_on_derive_monitor_off():
    exp, d = run_cb08_off()
    assert d.allow is True
    assert "SX" in exp.external


def test_cb09_two_secret_control_monitor_off():
    exp, d = run_cb09_off()
    assert d.allow is True
    assert "SY" in exp.external


def test_cb10_wrap_then_control_monitor_off():
    exp, d = run_cb10_off()
    assert d.allow is True
    assert "SZ" in exp.external
