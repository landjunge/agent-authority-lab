from .approval import ApprovalStore
from .audit import AuditLedger
from .models import ActionRequest, AuthorityDecision, Decision
from .store import WorkflowStore


IRREVERSIBLE = {"repo.delete", "release.publish"}
EXTERNAL = {"net.connect", "external.send"}


class AuthorityCore:
    def __init__(self, max_actions: int = 100):
        self.workflows = WorkflowStore()
        self.approvals = ApprovalStore()
        self.audit = AuditLedger()
        self.max_actions = max_actions

    def evaluate(self, req: ActionRequest, approval_id: str | None = None) -> AuthorityDecision:
        fp = req.fingerprint()
        self.audit.append("authority.requested", req.workflow_id, req.agent_id, fp, "REQUESTED")
        state = self.workflows.snapshot(req.workflow_id)

        if state.action_count >= self.max_actions:
            return self._decision(req, fp, Decision.DENY, "ACTION_BUDGET_EXCEEDED")

        if req.action in EXTERNAL:
            if any(state.value_labels.get(v) == "SENSITIVE" for v in req.input_value_ids):
                return self._decision(req, fp, Decision.DENY, "SENSITIVE_EXTERNAL_EGRESS")

        if req.action in IRREVERSIBLE:
            if approval_id and self.approvals.consume(approval_id, fp):
                self.workflows.commit_action(req.workflow_id)
                return self._decision(req, fp, Decision.ALLOW, "BOUND_APPROVAL_CONSUMED", approval_id)
            return self._decision(req, fp, Decision.REQUIRE_APPROVAL, "BOUND_APPROVAL_REQUIRED")

        self.workflows.commit_action(req.workflow_id)
        return self._decision(req, fp, Decision.ALLOW, "POLICY_ALLOW")

    def approve(self, req: ActionRequest, approver: str) -> str:
        approval = self.approvals.issue(req.fingerprint(), approver)
        self.audit.append("authority.approved", req.workflow_id, req.agent_id, req.fingerprint(), f"APPROVER:{approver}")
        return approval.approval_id

    def _decision(self, req, fp, decision, reason, approval_id=None):
        event = {
            Decision.ALLOW: "authority.allowed",
            Decision.DENY: "authority.denied",
            Decision.REQUIRE_APPROVAL: "authority.approval_required",
        }[decision]
        self.audit.append(event, req.workflow_id, req.agent_id, fp, reason)
        return AuthorityDecision(decision, reason, fp, approval_id)
