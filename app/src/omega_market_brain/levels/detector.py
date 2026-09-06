from __future__ import annotations
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import Iterable
from omega_market_brain.domain.models import Candle, Level

def _cluster(prices: list[Decimal], tolerance: Decimal) -> list[list[Decimal]]:
    if not prices:
        return []
    prices = sorted(prices)
    groups = [[prices[0]]]
    for p in prices[1:]:
        center = sum(groups[-1], Decimal("0")) / Decimal(len(groups[-1]))
        if abs(p - center) <= tolerance:
            groups[-1].append(p)
        else:
            groups.append([p])
    return groups

def detect_levels(
    candles: Iterable[Candle],
    *,
    current_price: Decimal,
    atr: Decimal,
    min_touches: int = 2,
    merge_atr_fraction: Decimal = Decimal("0.25"),
) -> tuple[Level | None, Level | None]:
    cs = list(candles)
    if not cs or atr <= 0:
        return None, None
    tolerance = atr * merge_atr_fraction
    highs = [c.high for c in cs]
    lows = [c.low for c in cs]
    high_clusters = [g for g in _cluster(highs, tolerance) if len(g) >= min_touches]
    low_clusters = [g for g in _cluster(lows, tolerance) if len(g) >= min_touches]

    resistances = []
    for g in high_clusters:
        price = sum(g, Decimal("0")) / Decimal(len(g))
        if price >= current_price:
            resistances.append(Level(price, "RESISTANCE", min(Decimal(len(g))/Decimal("5"), Decimal("1")), len(g)))

    supports = []
    for g in low_clusters:
        price = sum(g, Decimal("0")) / Decimal(len(g))
        if price <= current_price:
            supports.append(Level(price, "SUPPORT", min(Decimal(len(g))/Decimal("5"), Decimal("1")), len(g)))

    support = max(supports, key=lambda x: x.price) if supports else None
    resistance = min(resistances, key=lambda x: x.price) if resistances else None
    return support, resistance
