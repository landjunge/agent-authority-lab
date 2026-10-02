from service.adapter import TrustedAdapter
from service.blind_map import BLIND_MAP, Coverage
from service.gateway import AuthorityGateway
from service.models import ActionRequest, Decision


def req(action="file.read", resource="README.md", params=None, values=()):
    return ActionRequest("wf-1", "agent-a", action, resource, params or {}, values)


def test_normal_action_allows_and_audits():
    g = AuthorityGateway()
    d = g.submit(req())
    assert d.decision is Decision.ALLOW
    assert [e.event for e in g.core.audit.events()] == ["authority.requested", "authority.allowed"]


def test_irreversible_requires_bound_approval():
    g = AuthorityGateway()
    r = req("repo.delete", "repo")
    assert g.submit(r).decision is Decision.REQUIRE_APPROVAL
    approval = g.approve(r, "owner")
    assert g.submit(r, approval).decision is Decision.ALLOW


def test_approval_cannot_be_reused():
    g = AuthorityGateway()
    r = req("repo.delete", "repo")
    approval = g.approve(r, "owner")
    assert g.submit(r, approval).decision is Decision.ALLOW
    assert g.submit(r, approval).decision is Decision.REQUIRE_APPROVAL


def test_approval_cannot_authorize_different_action():
    g = AuthorityGateway()
    delete = req("repo.delete", "repo")
    publish = req("release.publish", "release")
    approval = g.approve(delete, "owner")
    assert g.submit(publish, approval).decision is Decision.REQUIRE_APPROVAL


def test_sensitive_provenance_blocks_external_egress():
    g = AuthorityGateway()
    g.core.workflows.bind_value("wf-1", "secret", "SENSITIVE")
    g.core.workflows.bind_value("wf-1", "derived", "PUBLIC", ("secret",))
    d = g.submit(req("external.send", "internet", values=("derived",)))
    assert d.decision is Decision.DENY
    assert d.reason == "SENSITIVE_EXTERNAL_EGRESS"


def test_denied_action_does_not_increment_budget():
    g = AuthorityGateway()
    g.core.workflows.bind_value("wf-1", "secret", "SENSITIVE")
    before = g.core.workflows.snapshot("wf-1").action_count
    g.submit(req("external.send", "internet", values=("secret",)))
    assert g.core.workflows.snapshot("wf-1").action_count == before


def test_action_budget_is_workflow_global():
    g = AuthorityGateway()
    g.core.max_actions = 2
    assert g.submit(req()).decision is Decision.ALLOW
    b = ActionRequest("wf-1", "agent-b", "file.read", "x")
    assert g.submit(b).decision is Decision.ALLOW
    assert g.submit(req()).decision is Decision.DENY


def test_adapter_refuses_non_allow_and_mismatched_request():
    g = AuthorityGateway()
    adapter = TrustedAdapter()
    r = req("repo.delete", "repo")
    pending = g.submit(r)
    assert adapter.execute(r, pending).executed is False

    allowed = g.submit(req())
    other = req("file.read", "OTHER")
    assert adapter.execute(other, allowed).executed is False


def test_blind_map_names_limits():
    assert BLIND_MAP["prompt_injection"] is Coverage.OUT_OF_MODEL
    assert BLIND_MAP["semantic_harm"] is Coverage.BLIND
    assert BLIND_MAP["approval_reuse"] is Coverage.DETECTED
