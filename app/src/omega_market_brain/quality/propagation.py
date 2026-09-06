from __future__ import annotations
from decimal import Decimal
from typing import Mapping
from omega_market_brain.domain.models import TimeframeState

def aggregate_quality(states: Mapping[str, TimeframeState]) -> Decimal:
    if not states:
        return Decimal("0")
    # Conservative: geometric-like penalty without floating point.
    values = [max(Decimal("0"), min(s.data_quality_score, Decimal("1"))) for s in states.values()]
    avg = sum(values, Decimal("0")) / Decimal(len(values))
    minimum = min(values)
    return avg * Decimal("0.7") + minimum * Decimal("0.3")
