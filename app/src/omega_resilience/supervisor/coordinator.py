from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from omega_resilience.domain.models import RecoveryState, ServiceClass
from omega_resilience.watchdog.restart_policy import restart_decision

@dataclass(frozen=True, slots=True)
class HealingAction:
    action: str
    service_id: str | None
    reason_codes: tuple[str,...]

def evaluate_service_failure(
    *,
    descriptor,
    system_state: RecoveryState,
    crash_loop: bool,
) -> tuple[HealingAction,...]:
    actions=[]
    if descriptor.service_class is ServiceClass.CRITICAL:
        actions.append(HealingAction("ENTER_SAFE",None,("RES_DEPENDENCY_DOWN",)))
    d=restart_decision(descriptor,system_state=system_state,crash_loop=crash_loop)
    if d.allowed and d.automatic:
        actions.append(HealingAction("RESTART_SERVICE",descriptor.service_id,d.reason_codes))
    elif d.reason_codes:
        actions.append(HealingAction("OPEN_INCIDENT",descriptor.service_id,d.reason_codes))
    return tuple(actions)
