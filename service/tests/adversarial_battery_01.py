"""Frozen Service v0.1 Adversarial Battery 01 baseline.

These tests encode the secure oracle and are expected to expose current misses.
Do not weaken them to make CI green.
"""
from service.adapter import TrustedAdapter
from service.gateway import AuthorityGateway
from service.models import ActionRequest, Decision


def r(action, resource="x", params=None, values=()):
    return ActionRequest("wf-ab01", "agent-a", action, resource, params or {}, values)


def test_ab01_unknown_powerful_action_must_not_reach_adapter():
    g = AuthorityGateway()
    adapter = TrustedAdapter()
    req = r("future.powerful.effect", "critical-system")
    decision = g.submit(req)
    assert decision.decision is Decision.DENY
    assert adapter.execute(req, decision).executed is False


def test_ab02_unmodeled_implicit_secret_bit_must_not_egress():
    g = AuthorityGateway()
    g.core.workflows.bind_value("wf-ab01", "secret", "SENSITIVE")
    g.core.workflows.bind_value("wf-ab01", "status", "PUBLIC")
    req = r("external.send", "internet", {"payload": "1"}, values=("status",))
    assert g.submit(req).decision is Decision.DENY


def test_ab03_explicitly_harmful_modeled_intent_must_not_execute():
    g = AuthorityGateway()
    adapter = TrustedAdapter()
    req = r("file.read", "public.txt", {"intent": "harmful"})
    decision = g.submit(req)
    assert decision.decision is Decision.DENY
    assert adapter.execute(req, decision).executed is False


def test_ab04_modeled_untrusted_instruction_marker_must_not_pass():
    g = AuthorityGateway()
    req = r("file.read", "README.md", {"untrusted_instruction": True})
    assert g.submit(req).decision is Decision.DENY
