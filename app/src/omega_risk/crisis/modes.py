from __future__ import annotations
from decimal import Decimal
from omega_risk.domain.models import CrisisMode

MULTIPLIERS = {
    CrisisMode.NORMAL: Decimal("1.00"),
    CrisisMode.CAUTION: Decimal("0.60"),
    CrisisMode.DEFENSIVE: Decimal("0.30"),
    CrisisMode.SAFE: Decimal("0.00"),
    CrisisMode.EMERGENCY: Decimal("0.00"),
}

def risk_multiplier(mode: CrisisMode) -> Decimal:
    return MULTIPLIERS[mode]

def mode_blocks_new_entries(mode: CrisisMode) -> bool:
    return mode in {CrisisMode.SAFE, CrisisMode.EMERGENCY}

def mode_reason(mode: CrisisMode) -> str | None:
    if mode is CrisisMode.SAFE:
        return "RISK_CRISIS_SAFE"
    if mode is CrisisMode.EMERGENCY:
        return "RISK_CRISIS_EMERGENCY"
    return None
