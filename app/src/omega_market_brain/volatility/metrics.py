from __future__ import annotations
from decimal import Decimal, getcontext
from typing import Iterable
from omega_market_brain.domain.models import Candle

getcontext().prec = 28

def true_ranges(candles: Iterable[Candle]) -> list[Decimal]:
    cs = list(candles)
    if not cs:
        return []
    out = []
    prev_close = cs[0].close
    for c in cs:
        tr = max(
            c.high - c.low,
            abs(c.high - prev_close),
            abs(c.low - prev_close),
        )
        out.append(tr)
        prev_close = c.close
    return out

def atr(candles: Iterable[Candle], period: int = 14) -> Decimal | None:
    trs = true_ranges(candles)
    if not trs:
        return None
    xs = trs[-period:]
    return sum(xs, Decimal("0")) / Decimal(len(xs))

def atr_pct(candles: Iterable[Candle], period: int = 14) -> Decimal | None:
    cs = list(candles)
    if not cs:
        return None
    a = atr(cs, period)
    if a is None or cs[-1].close == 0:
        return None
    return a / cs[-1].close

def realized_vol_proxy(candles: Iterable[Candle], period: int = 20) -> Decimal | None:
    cs = list(candles)
    if len(cs) < 2:
        return None
    rets = []
    for a, b in zip(cs[:-1], cs[1:]):
        if a.close == 0:
            continue
        rets.append((b.close - a.close) / a.close)
    xs = rets[-period:]
    if not xs:
        return None
    mean = sum(xs, Decimal("0")) / Decimal(len(xs))
    variance = sum((x - mean) ** 2 for x in xs) / Decimal(len(xs))
    # Decimal sqrt
    return variance.sqrt()
