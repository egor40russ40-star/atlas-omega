CRITICAL_ACTIONS = (
    "SAFE_PAUSE",
    "ENTER_SAFE",
    "EMERGENCY_STOP",
)

def requires_explicit_tap(command_type: str) -> bool:
    return command_type in CRITICAL_ACTIONS

def gesture_only_allowed(command_type: str) -> bool:
    # No financial/safety-changing action can be gesture-only.
    return False if command_type in CRITICAL_ACTIONS else False
