from __future__ import annotations
from decimal import Decimal

def resolve_stop_take_same_bar(
    *,
    side: str,
    bar_open: Decimal,
    bar_high: Decimal,
    bar_low: Decimal,
    stop_price: Decimal,
    take_price: Decimal,
    policy: str = "ADVERSE_FIRST",
) -> tuple[str, Decimal] | None:
    if side=="BUY":
        stop_hit = bar_low <= stop_price
        take_hit = bar_high >= take_price
    else:
        stop_hit = bar_high >= stop_price
        take_hit = bar_low <= take_price

    if stop_hit and take_hit:
        if policy=="ADVERSE_FIRST":
            return "STOP",stop_price
        if policy=="FAVORABLE_FIRST":
            return "TAKE_PROFIT",take_price
        raise ValueError("ambiguous bar path")
    if stop_hit:
        return "STOP",stop_price
    if take_hit:
        return "TAKE_PROFIT",take_price
    return None
