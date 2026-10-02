from dataclasses import dataclass
from .models import ActionRequest, AuthorityDecision, Decision


@dataclass(frozen=True)
class ExecutionReceipt:
    fingerprint: str
    executed: bool


class TrustedAdapter:
    """Reference adapter proving decision/request binding before execution."""

    def execute(self, request: ActionRequest, decision: AuthorityDecision) -> ExecutionReceipt:
        if decision.decision is not Decision.ALLOW:
            return ExecutionReceipt(request.fingerprint(), False)
        if decision.request_fingerprint != request.fingerprint():
            return ExecutionReceipt(request.fingerprint(), False)
        # v0.1 intentionally performs no real side effect.
        return ExecutionReceipt(request.fingerprint(), True)
