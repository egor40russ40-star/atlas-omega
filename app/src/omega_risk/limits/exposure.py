from __future__ import annotations
from decimal import Decimal

def would_exceed(current: Decimal, increment: Decimal, limit: Decimal | None) -> bool:
    if limit is None:
        return False
    return current + increment > limit

def concentration_pct(instrument_exposure: Decimal, portfolio_equity: Decimal) -> Decimal:
    if portfolio_equity <= 0:
        return Decimal("1")
    return abs(instrument_exposure) / portfolio_equity

def concentration_exceeded(
    instrument_exposure: Decimal,
    added_capital: Decimal,
    portfolio_equity: Decimal,
    max_pct: Decimal | None
) -> bool:
    if max_pct is None:
        return False
    return concentration_pct(instrument_exposure + added_capital, portfolio_equity) > max_pct
