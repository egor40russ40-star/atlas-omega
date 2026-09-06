from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True, slots=True)
class SafetyInput:
    approvals_present: bool
    approval_hash_matches: bool
    approval_valid_until: datetime
    market_data_fresh: bool
    broker_reconciled: bool
    kill_switch: bool
    recovery_in_progress: bool

def validate_safety(inp: SafetyInput, now: datetime | None = None) -> list[str]:
    now = now or datetime.now(timezone.utc)
    reasons: list[str] = []
    if not inp.approvals_present:
        reasons.append("APPROVAL_HASH_MISMATCH")
    if not inp.approval_hash_matches:
        reasons.append("APPROVAL_HASH_MISMATCH")
    if inp.approval_valid_until <= now:
        reasons.append("APPROVAL_EXPIRED")
    if not inp.market_data_fresh:
        reasons.append("STALE_MARKET_DATA")
    if not inp.broker_reconciled:
        reasons.append("BROKER_STATE_STALE")
    if inp.kill_switch:
        reasons.append("KILL_SWITCH_ACTIVE")
    if inp.recovery_in_progress:
        reasons.append("RECOVERY_IN_PROGRESS")
    return sorted(set(reasons))
