from __future__ import annotations
from decimal import Decimal
from omega_market_brain.domain.models import Direction

def classify_direction(score: Decimal) -> Direction:
    if score <= Decimal("-0.65"):
        return Direction.STRONG_DOWN
    if score <= Decimal("-0.20"):
        return Direction.DOWN
    if score < Decimal("0.20"):
        return Direction.NEUTRAL
    if score < Decimal("0.65"):
        return Direction.UP
    return Direction.STRONG_UP

def direction_from_returns(
    short_return: Decimal,
    medium_return: Decimal,
    long_return: Decimal,
) -> Decimal:
    score = short_return * Decimal("0.2") + medium_return * Decimal("0.3") + long_return * Decimal("0.5")
    # compress to [-1, 1] without math dependency
    if score > 1:
        return Decimal("1")
    if score < -1:
        return Decimal("-1")
    return score
