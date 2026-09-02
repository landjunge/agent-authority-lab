from __future__ import annotations

from typing import Any

from lab.fake_repo import FakeRepo
from lab.models import ActionRequest, Decision
from lab.paths import canonical_path
from lab.validator import Lab


class FakeAdapter:
    """Local action surface. No sockets, no real git, no credentials."""

    def __init__(self, lab: Lab | None = None) -> None:
        self.lab = lab or Lab()
        self.repo = FakeRepo()

    def write(self, actor: str, path: str, workflow_id: str, content: str = "") -> Decision:
        _ = content  # not persisted on deny; repo only updates on allow
        path = canonical_path(path) or path
        d = self.lab.submit(
            ActionRequest(actor, "file.write", path, {}, workflow_id)
        )
        if d.allow:
            self.repo.files[path] = content
        return d

    def read(self, actor: str, path: str, workflow_id: str) -> Decision:
        path = canonical_path(path) or path
        return self.lab.submit(
            ActionRequest(actor, "file.read", path, {}, workflow_id)
        )

    def delete(
        self, actor: str, path: str, workflow_id: str, approval_token: Any = None
    ) -> Decision:
        path = canonical_path(path) or path
        params: dict[str, Any] = {}
        if approval_token is not None:
            params["approval_token"] = approval_token
        d = self.lab.submit(
            ActionRequest(actor, "file.delete", path, params, workflow_id)
        )
        if d.allow:
            self.repo.files.pop(path, None)
        return d

    def delegate(self, actor: str, to: str, workflow_id: str) -> Decision:
        return self.lab.submit(
            ActionRequest(actor, "delegate", to, {"to": to}, workflow_id)
        )

    def net_connect(self, actor: str, destination: str, workflow_id: str) -> Decision:
        return self.lab.submit(
            ActionRequest(
                actor, "net.connect", destination, {"destination": destination}, workflow_id
            )
        )

    def irreversible(
        self, actor: str, action: str, workflow_id: str, approval_token: Any = None
    ) -> Decision:
        params: dict[str, Any] = {}
        if approval_token is not None:
            params["approval_token"] = approval_token
        return self.lab.submit(ActionRequest(actor, action, action, params, workflow_id))
