from __future__ import annotations
from decimal import Decimal

def current_day_pnl(realized: Decimal, unrealized: Decimal) -> Decimal:
    return realized + unrealized

def drawdown_rub(equity: Decimal, high_water: Decimal) -> Decimal:
    return max(high_water - equity, Decimal("0"))

def check_daily_loss(realized: Decimal, unrealized: Decimal, limit: Decimal | None) -> bool:
    if limit is None:
        return False
    return current_day_pnl(realized, unrealized) <= -abs(limit)

def check_drawdown(equity: Decimal, high_water: Decimal, limit: Decimal | None) -> bool:
    if limit is None:
        return False
    return drawdown_rub(equity, high_water) >= abs(limit)
