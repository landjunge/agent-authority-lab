from enum import Enum


class Coverage(str, Enum):
    DETECTED = "DETECTED"
    PARTIAL = "PARTIAL"
    BLIND = "BLIND"
    OUT_OF_MODEL = "OUT_OF_MODEL"


BLIND_MAP = {
    "workflow_action_budget": Coverage.DETECTED,
    "sensitive_explicit_egress": Coverage.DETECTED,
    "cross_agent_provenance": Coverage.PARTIAL,
    "approval_reuse": Coverage.DETECTED,
    "unmodeled_implicit_flow": Coverage.BLIND,
    "prompt_injection": Coverage.OUT_OF_MODEL,
    "timing_channel": Coverage.OUT_OF_MODEL,
    "covert_channel": Coverage.OUT_OF_MODEL,
    "semantic_harm": Coverage.BLIND,
    "compromised_runtime": Coverage.OUT_OF_MODEL,
    "distributed_multi_process_consistency": Coverage.OUT_OF_MODEL,
    "tamper_evident_audit_storage": Coverage.OUT_OF_MODEL,
}
