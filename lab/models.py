from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

PROTECTED_PATH = "config/security-policy.json"
WRITE_ACTIONS = frozenset({"file.write"})
DELETE_ACTIONS = frozenset({"file.delete"})
# I8 frozen mutating-verb set. Not a global action taxonomy.
MUTATING_ACTIONS = frozenset(
    {"file.write", "file.delete", "file.remove", "file.rename", "file.unlink"}
)
NETWORK_ACTIONS = frozenset({"net.connect"})
DELEGATE_ACTIONS = frozenset({"delegate"})
IRREVERSIBLE_ACTIONS = frozenset({"repo.delete", "release.publish"})
# I9: exact known/safe vocabulary. No case folding. Not a blacklist of aliases.
KNOWN_ACTIONS = frozenset(
    {
        "file.read",
        "file.write",
        "file.delete",
        "file.remove",
        "file.rename",
        "file.unlink",
        "delegate",
        "net.connect",
        "repo.delete",
        "release.publish",
    }
)

I1_ACTION_BUDGET = "I1_ACTION_BUDGET"
I2_FILE_LIMIT = "I2_FILE_LIMIT"
I3_PROTECTED_PATH = "I3_PROTECTED_PATH"
I4_DELEGATION_DEPTH = "I4_DELEGATION_DEPTH"
I5_NETWORK = "I5_NETWORK"
I6_IRREVERSIBLE = "I6_IRREVERSIBLE"
I7_SECURITY_TEST_DELETE = "I7_SECURITY_TEST_DELETE"
I8_PROTECTED_MUTATION = "I8_PROTECTED_MUTATION"
I9_UNKNOWN_ACTION_PROTECTED = "I9_UNKNOWN_ACTION_PROTECTED"
INVALID_REQUEST = "INVALID_REQUEST"

MAX_REQUEST_FIELD = 256

MAX_ACTIONS = 100
MAX_UNIQUE_FILES = 10
MAX_DELEGATION_DEPTH = 1


@dataclass
class ProvenanceRecord:
    workflow_id: str
    actor: str
    action: str
    resource: str
    decision: str
    state_before: dict[str, Any]
    state_after: dict[str, Any]
    timestamp: str
    seq: int


@dataclass
class WorkflowState:
    workflow_id: str
    action_count: int = 0
    files_changed: int = 0
    touched_paths: set[str] = field(default_factory=set)
    agents: set[str] = field(default_factory=set)
    delegation_depth: int = 0
    network_destinations: set[str] = field(default_factory=set)
    irreversible_effects: list[str] = field(default_factory=list)
    provenance: list[ProvenanceRecord] = field(default_factory=list)
    # Internal bookkeeping for I4. Root depth is 0.
    actor_depth: dict[str, int] = field(default_factory=dict)

    def snapshot(self) -> WorkflowState:
        return WorkflowState(
            workflow_id=self.workflow_id,
            action_count=self.action_count,
            files_changed=self.files_changed,
            touched_paths=set(self.touched_paths),
            agents=set(self.agents),
            delegation_depth=self.delegation_depth,
            network_destinations=set(self.network_destinations),
            irreversible_effects=list(self.irreversible_effects),
            provenance=list(self.provenance),
            actor_depth=dict(self.actor_depth),
        )

    def public_view(self) -> dict[str, Any]:
        """Serializable spec fields only. No provenance payload, no secrets."""
        return {
            "workflow_id": self.workflow_id,
            "action_count": self.action_count,
            "files_changed": self.files_changed,
            "touched_paths": sorted(self.touched_paths),
            "agents": sorted(self.agents),
            "delegation_depth": self.delegation_depth,
            "network_destinations": sorted(self.network_destinations),
            "irreversible_effects": list(self.irreversible_effects),
        }


@dataclass
class ActionRequest:
    actor: str
    action: str
    resource: str
    parameters: dict[str, Any]
    workflow_id: str


@dataclass
class Decision:
    allow: bool
    deny_reason: str | None
    violated_invariants: list[str]
