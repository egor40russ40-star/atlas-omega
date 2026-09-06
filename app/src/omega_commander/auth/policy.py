from __future__ import annotations
from omega_commander.domain.models import Role, CommandType, CommandDecision

PERMANENTLY_FORBIDDEN = {
    CommandType.DISABLE_RISK_GOVERNOR,
    CommandType.DISABLE_SAFETY_KERNEL,
    CommandType.BYPASS_RECONCILIATION,
    CommandType.DIRECT_BROKER_ORDER,
    CommandType.DELETE_FINANCIAL_AUDIT,
    CommandType.FORCE_LIVE_UNVERIFIED_STRATEGY,
}

DANGEROUS = {
    CommandType.ENTER_SAFE,
    CommandType.EMERGENCY_STOP,
    CommandType.RESTART_CRITICAL_SERVICE,
    CommandType.RESUME_TRADING,
}

ROLE_ALLOW = {
    Role.VIEWER: set(),
    Role.OPERATOR: {
        CommandType.SAFE_PAUSE,
        CommandType.ENTER_SAFE,
        CommandType.ACK_INCIDENT,
        CommandType.RESTART_NONCRITICAL_SERVICE,
    },
    Role.ADMIN: {
        CommandType.SAFE_PAUSE,
        CommandType.ENTER_SAFE,
        CommandType.EMERGENCY_STOP,
        CommandType.RESUME_TRADING,
        CommandType.ACK_INCIDENT,
        CommandType.RESTART_NONCRITICAL_SERVICE,
        CommandType.RESTART_CRITICAL_SERVICE,
        CommandType.UPDATE_OPERATIONAL_SETTING,
    },
    Role.SYSTEM: {
        CommandType.SAFE_PAUSE,
        CommandType.ENTER_SAFE,
        CommandType.ACK_INCIDENT,
        CommandType.RESTART_NONCRITICAL_SERVICE,
    },
}

def authorize(role: Role, command_type: CommandType) -> CommandDecision:
    if command_type in PERMANENTLY_FORBIDDEN:
        return CommandDecision(False,False,("CMD_PERMANENTLY_FORBIDDEN",))
    if command_type not in ROLE_ALLOW[role]:
        return CommandDecision(False,False,("CMD_ROLE_DENIED",))
    return CommandDecision(True,command_type in DANGEROUS,())
