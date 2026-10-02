from dataclasses import dataclass, field
from threading import RLock


@dataclass
class WorkflowState:
    action_count: int = 0
    value_labels: dict[str, str] = field(default_factory=dict)
    provenance: dict[str, tuple[str, ...]] = field(default_factory=dict)


class WorkflowStore:
    def __init__(self):
        self._lock = RLock()
        self._states: dict[str, WorkflowState] = {}

    def get(self, workflow_id: str) -> WorkflowState:
        with self._lock:
            return self._states.setdefault(workflow_id, WorkflowState())

    def snapshot(self, workflow_id: str) -> WorkflowState:
        with self._lock:
            s = self._states.get(workflow_id, WorkflowState())
            return WorkflowState(s.action_count, dict(s.value_labels), dict(s.provenance))

    def commit_action(self, workflow_id: str) -> None:
        with self._lock:
            self.get(workflow_id).action_count += 1

    def bind_value(self, workflow_id: str, value_id: str, label: str, derived_from: tuple[str, ...] = ()) -> None:
        with self._lock:
            s = self.get(workflow_id)
            inherited = any(s.value_labels.get(v) == "SENSITIVE" for v in derived_from)
            s.value_labels[value_id] = "SENSITIVE" if label == "SENSITIVE" or inherited else "PUBLIC"
            s.provenance[value_id] = derived_from
