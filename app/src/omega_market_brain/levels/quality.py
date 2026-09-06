from __future__ import annotations
from decimal import Decimal
from omega_market_brain.domain.models import Level

def ambiguity_score(support: Level | None, resistance: Level | None, *, atr: Decimal | None) -> Decimal:
    if support is None or resistance is None:
        return Decimal("1")
    if atr is None or atr <= 0:
        return Decimal("0.5")
    width = resistance.price - support.price
    if width <= 0:
        return Decimal("1")
    ratio = width / atr
    if ratio < Decimal("0.5"):
        return Decimal("0.9")
    if ratio < Decimal("1"):
        return Decimal("0.6")
    if support.strength < Decimal("0.4") or resistance.strength < Decimal("0.4"):
        return Decimal("0.5")
    return Decimal("0.1")
