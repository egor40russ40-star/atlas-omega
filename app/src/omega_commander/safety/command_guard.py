from __future__ import annotations
from omega_commander.domain.models import CommandType

CRITICAL_SERVICES = {
    "omega-risk",
    "omega-safety",
    "omega-execution",
    "omega-broker-state",
    "omega-capital",
}

NONCRITICAL_SERVICES = {
    "omega-research",
    "omega-ai-lab",
    "omega-replay",
    "omega-dashboard",
    "omega-news",
}

def contextual_reasons(command, system_status) -> list[str]:
    reasons=[]
    ct=command.command_type

    if ct is CommandType.RESUME_TRADING:
        if system_status.operational_state != "READY":
            reasons.append("CMD_RESUME_DENIED_NOT_READY")
        if system_status.kill_switch_active:
            reasons.append("CMD_RESUME_DENIED_KILL_SWITCH")
        if system_status.reconciliation_status not in {"OK","WARNING"}:
            reasons.append("CMD_RESUME_DENIED_NOT_READY")
        if not system_status.market_data_fresh or not system_status.broker_connected:
            reasons.append("CMD_RESUME_DENIED_NOT_READY")

    if ct is CommandType.RESTART_CRITICAL_SERVICE:
        if command.target not in CRITICAL_SERVICES:
            reasons.append("CMD_TARGET_NOT_ALLOWED")
        if system_status.operational_state not in {"SAFE","RECOVERY"}:
            reasons.append("CMD_CRITICAL_RESTART_REQUIRES_SAFE")

    if ct is CommandType.RESTART_NONCRITICAL_SERVICE:
        if command.target not in NONCRITICAL_SERVICES:
            reasons.append("CMD_TARGET_NOT_ALLOWED")

    return sorted(set(reasons))
