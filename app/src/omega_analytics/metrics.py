from typing import Iterable

from .models import TradeRecord


def total_trades(trades: Iterable[TradeRecord]) -> int:
    return len(list(trades))


def win_rate(trades: Iterable[TradeRecord]) -> float:
    items = list(trades)

    if not items:
        return 0.0

    wins = [
        t for t in items
        if t.pnl is not None and t.pnl > 0
    ]

    return len(wins) / len(items)