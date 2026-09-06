from __future__ import annotations
from dataclasses import dataclass
from omega_resilience.domain.models import ServiceClass, RecoveryState, ServiceDescriptor

@dataclass(frozen=True, slots=True)
class RestartDecision:
    allowed: bool
    automatic: bool
    requires_safe: bool
    reason_codes: tuple[str,...]

def restart_decision(
    descriptor: ServiceDescriptor,
    *,
    system_state: RecoveryState,
    crash_loop: bool,
) -> RestartDecision:
    if crash_loop:
        return RestartDecision(False,False,descriptor.restart_requires_safe,("RES_CRASH_LOOP",))
    if descriptor.service_class is ServiceClass.CRITICAL and system_state is RecoveryState.LIVE:
        return RestartDecision(False,False,True,("RES_CRITICAL_RESTART_BLOCKED_IN_LIVE",))
    if descriptor.restart_requires_safe and system_state not in {RecoveryState.SAFE,RecoveryState.RECOVERY,RecoveryState.BOOT,RecoveryState.SELF_TEST}:
        return RestartDecision(False,False,True,("RES_CRITICAL_RESTART_BLOCKED_IN_LIVE",))
    if not descriptor.auto_restart_allowed:
        return RestartDecision(False,False,descriptor.restart_requires_safe,())
    return RestartDecision(True,True,descriptor.restart_requires_safe,())
