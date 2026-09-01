PUBLIC = "PUBLIC"
SENSITIVE = "SENSITIVE"


def join_labels(labels: list[str]) -> str:
    if any(label == SENSITIVE for label in labels):
        return SENSITIVE
    return PUBLIC
