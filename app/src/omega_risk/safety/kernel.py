from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from omega_risk.safety.authorization import SafetyAuthorization, validate_authorization

@dataclass(frozen=True, slots=True)
class SafetyContext:
    system_state: str
    reconciliation_status: str
    market_data_fresh: bool
    broker_state_fresh: bool
    kill_switch_active: bool

def safety_reasons(auth: SafetyAuthorization, ctx: SafetyContext, *, now: datetime | None = None) -> list[str]:
    reasons = validate_authorization(auth, now=now)

    if ctx.kill_switch_active:
        reasons.append("RISK_KILL_SWITCH_ACTIVE")
    if ctx.system_state in {"SAFE", "EMERGENCY", "RECOVERY"}:
        reasons.append("RISK_CRISIS_SAFE" if ctx.system_state != "EMERGENCY" else "RISK_CRISIS_EMERGENCY")
    if ctx.reconciliation_status in {"BLOCKING", "CRITICAL"}:
        reasons.append("RISK_RECONCILIATION_BLOCK")
    if not ctx.market_data_fresh:
        reasons.append("RISK_STALE_MARKET_DATA")
    if not ctx.broker_state_fresh:
        reasons.append("RISK_STALE_BROKER_STATE")
    return sorted(set(reasons))

def authorized(auth: SafetyAuthorization, ctx: SafetyContext, *, now: datetime | None = None) -> bool:
    return not safety_reasons(auth, ctx, now=now)
