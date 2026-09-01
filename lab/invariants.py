from __future__ import annotations

from lab.models import (
    I1_ACTION_BUDGET,
    I2_FILE_LIMIT,
    I3_PROTECTED_PATH,
    I4_DELEGATION_DEPTH,
    I5_NETWORK,
    I6_IRREVERSIBLE,
    IRREVERSIBLE_ACTIONS,
    MAX_ACTIONS,
    MAX_DELEGATION_DEPTH,
    MAX_UNIQUE_FILES,
    PROTECTED_PATH,
    WRITE_ACTIONS,
    ActionRequest,
    WorkflowState,
)


def evaluate(req: ActionRequest, predicted: WorkflowState) -> list[str]:
    """Return violated invariant IDs. No LLM. No semantic intent."""
    violated: list[str] = []

    if predicted.action_count > MAX_ACTIONS:
        violated.append(I1_ACTION_BUDGET)

    if predicted.files_changed > MAX_UNIQUE_FILES:
        violated.append(I2_FILE_LIMIT)

    if req.action in WRITE_ACTIONS and req.resource == PROTECTED_PATH:
        violated.append(I3_PROTECTED_PATH)

    if predicted.delegation_depth > MAX_DELEGATION_DEPTH:
        violated.append(I4_DELEGATION_DEPTH)

    if predicted.network_destinations:
        violated.append(I5_NETWORK)

    if req.action in IRREVERSIBLE_ACTIONS and not req.parameters.get("approval_token"):
        violated.append(I6_IRREVERSIBLE)

    return violated
