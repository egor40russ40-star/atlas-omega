from __future__ import annotations
from decimal import Decimal
from typing import Mapping
from omega_market_brain.domain.models import TimeframeState

WEIGHTS = {
    "1D": Decimal("0.25"),
    "4h": Decimal("0.20"),
    "1h": Decimal("0.20"),
    "15m": Decimal("0.15"),
    "5m": Decimal("0.12"),
    "1m": Decimal("0.08"),
}

def weighted_bias(states: Mapping[str, TimeframeState]) -> Decimal:
    num = Decimal("0")
    den = Decimal("0")
    for tf, s in states.items():
        w = WEIGHTS.get(tf, Decimal("0"))
        q = max(min(s.data_quality_score, Decimal("1")), Decimal("0"))
        effective = w * q
        num += s.direction_score * effective
        den += effective
    return Decimal("0") if den == 0 else num / den

def conflict_score(states: Mapping[str, TimeframeState]) -> Decimal:
    if not states:
        return Decimal("1")
    bias = weighted_bias(states)
    num = Decimal("0")
    den = Decimal("0")
    for tf, s in states.items():
        w = WEIGHTS.get(tf, Decimal("0"))
        q = max(min(s.data_quality_score, Decimal("1")), Decimal("0"))
        effective = w * q
        # max distance in [-1,1] is 2 -> normalize to [0,1]
        num += abs(s.direction_score - bias) / Decimal("2") * effective
        den += effective
    if den == 0:
        return Decimal("1")
    return min(num / den, Decimal("1"))
