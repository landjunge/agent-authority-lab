"""AuthorityOK(actor, action, resource). No labels. No provenance."""

AGENT_A = "agent-a"
AGENT_B = "agent-b"

CUSTOMERS = "fake://customers"
WORKFLOW_MSG = "workflow://message"
WORKFLOW_STATE = "workflow://state"
EXTERNAL = "https://external.example"

CUSTOMER_READ = "customer.read"
WORKFLOW_SEND = "workflow.send"
WORKFLOW_RECEIVE = "workflow.receive"
EXTERNAL_SEND = "external.send"
PUBLIC_WRITE = "public.write"
STATE_WRITE = "workflow.state.write"
STATE_READ = "workflow.state.read"
COPY = "copy"
DERIVE = "derive"
WRAP = "wrap"
CONTROL_DECIDE = "control.decide"

_ACTORS = frozenset({AGENT_A, AGENT_B})
_INTERNAL = frozenset({COPY, DERIVE, WRAP, CONTROL_DECIDE})
_CHANNEL = frozenset({WORKFLOW_SEND, WORKFLOW_RECEIVE, PUBLIC_WRITE})


def authority_ok(actor: str, action: str, resource: str) -> bool:
    if actor not in _ACTORS:
        return False
    if action in _INTERNAL:
        return True
    if action == CUSTOMER_READ and resource == CUSTOMERS:
        return actor == AGENT_A
    if action in _CHANNEL and resource == WORKFLOW_MSG:
        return True
    if action == STATE_WRITE and resource == WORKFLOW_STATE:
        return actor == AGENT_A
    if action == STATE_READ and resource == WORKFLOW_STATE:
        return actor == AGENT_B
    if action == EXTERNAL_SEND and resource == EXTERNAL:
        return actor == AGENT_B
    return False
