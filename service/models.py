from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any


class Decision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


@dataclass(frozen=True)
class ActionRequest:
    workflow_id: str
    agent_id: str
    action: str
    resource: str
    parameters: dict[str, Any] = field(default_factory=dict)
    input_value_ids: tuple[str, ...] = ()

    def fingerprint(self) -> str:
        payload = {
            "workflow_id": self.workflow_id,
            "agent_id": self.agent_id,
            "action": self.action,
            "resource": self.resource,
            "parameters": self.parameters,
            "input_value_ids": list(self.input_value_ids),
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(raw.encode()).hexdigest()


@dataclass(frozen=True)
class AuthorityDecision:
    decision: Decision
    reason: str
    request_fingerprint: str
    approval_id: str | None = None
