TRIGGERS = {
    "ORDER_SUBMIT",
    "ORDER_REJECTED",
    "UNKNOWN_OUTCOME",
    "PARTIAL_FILL",
    "CANCEL_RACE",
    "POSITION_MISMATCH",
    "UNEXPECTED_BROKER_ORDER",
    "RECOVERY_REQUIRED",
}

def should_capture(trigger: str) -> bool:
    return trigger in TRIGGERS
