from __future__ import annotations

from lab.models import (
    DELEGATE_ACTIONS,
    IRREVERSIBLE_ACTIONS,
    NETWORK_ACTIONS,
    WRITE_ACTIONS,
    ActionRequest,
    WorkflowState,
)
from lab.paths import canonical_path


def empty_state(workflow_id: str) -> WorkflowState:
    return WorkflowState(workflow_id=workflow_id)


def predict_next(state: WorkflowState, req: ActionRequest) -> WorkflowState:
    """Pure prediction. Does not mutate `state`."""
    nxt = state.snapshot()
    nxt.action_count += 1
    nxt.agents.add(req.actor)
    if req.actor not in nxt.actor_depth:
        nxt.actor_depth[req.actor] = 0

    if req.action in WRITE_ACTIONS:
        nxt.touched_paths.add(canonical_path(req.resource) or req.resource)
        nxt.files_changed = len(nxt.touched_paths)

    if req.action in NETWORK_ACTIONS:
        dest = str(req.parameters.get("destination") or req.resource)
        nxt.network_destinations.add(dest)

    if req.action in DELEGATE_ACTIONS:
        target = str(req.parameters.get("to") or req.resource)
        parent = nxt.actor_depth.get(req.actor, 0)
        nxt.actor_depth[target] = parent + 1
        nxt.delegation_depth = max(nxt.actor_depth.values(), default=0)

    if req.action in IRREVERSIBLE_ACTIONS:
        nxt.irreversible_effects.append(req.action)

    nxt.delegation_depth = max(nxt.actor_depth.values(), default=0)
    return nxt
