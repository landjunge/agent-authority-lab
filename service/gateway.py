from .core import AuthorityCore
from .models import ActionRequest, AuthorityDecision


class AuthorityGateway:
    """Single application-facing entry point for authority decisions."""

    def __init__(self, core: AuthorityCore | None = None):
        self.core = core or AuthorityCore()

    def submit(self, request: ActionRequest, approval_id: str | None = None) -> AuthorityDecision:
        return self.core.evaluate(request, approval_id)

    def approve(self, request: ActionRequest, approver: str) -> str:
        return self.core.approve(request, approver)
