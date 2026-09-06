from __future__ import annotations

CRITICAL_SERVICES = {
    "omega-risk",
    "omega-safety",
    "omega-execution",
    "omega-capital",
    "omega-broker-state",
}

def watchdog_action(service_name: str, heartbeat_ok: bool) -> str:
    if heartbeat_ok:
        return "NONE"
    if service_name in {"omega-risk", "omega-safety"}:
        return "FAIL_CLOSED"
    if service_name in {"omega-execution", "omega-broker-state"}:
        return "SAFE_RECOVERY"
    if service_name in CRITICAL_SERVICES:
        return "SAFE"
    return "RESTART_NONCRITICAL"
