"""Monitor-off harness for the convergence battery. No evaluate. No Lab.submit."""

from __future__ import annotations

from lab.models import ActionRequest, WorkflowState
from lab.state import empty_state, predict_next


def phase1_off(steps: list[ActionRequest]) -> dict[str, WorkflowState]:
    """Apply predict_next per workflow_id. Does not call evaluate or Lab.submit."""
    states: dict[str, WorkflowState] = {}
    for req in steps:
        current = states.get(req.workflow_id) or empty_state(req.workflow_id)
        states[req.workflow_id] = predict_next(current, req)
    return states
