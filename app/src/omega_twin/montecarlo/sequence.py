from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
import random
from typing import Sequence

@dataclass(frozen=True, slots=True)
class MonteCarloPath:
    final_r: Decimal
    max_drawdown_r: Decimal
    max_losing_streak: int

@dataclass(frozen=True, slots=True)
class MonteCarloSummary:
    simulations: int
    p50_final_r: Decimal
    p05_final_r: Decimal
    p95_drawdown_r: Decimal
    p95_losing_streak: int

def _path(xs: Sequence[Decimal]) -> MonteCarloPath:
    equity=Decimal("0")
    high=Decimal("0")
    dd=Decimal("0")
    cur=best=0
    for x in xs:
        equity+=x
        high=max(high,equity)
        dd=max(dd,high-equity)
        if x<0:
            cur+=1; best=max(best,cur)
        else:
            cur=0
    return MonteCarloPath(equity,dd,best)

def _quantile(values, q: float):
    xs=sorted(values)
    if not xs:
        return None
    idx=min(len(xs)-1,max(0,int(round((len(xs)-1)*q))))
    return xs[idx]

def simulate(
    trade_rs: Sequence[Decimal],
    *,
    simulations: int,
    seed: int,
    method: str = "bootstrap",
) -> MonteCarloSummary:
    if not trade_rs:
        return MonteCarloSummary(0,Decimal("0"),Decimal("0"),Decimal("0"),0)
    rng=random.Random(seed)
    paths=[]
    for _ in range(simulations):
        if method=="permutation":
            xs=list(trade_rs)
            rng.shuffle(xs)
        elif method=="bootstrap":
            xs=[trade_rs[rng.randrange(len(trade_rs))] for _ in range(len(trade_rs))]
        else:
            raise ValueError("unknown monte carlo method")
        paths.append(_path(xs))
    return MonteCarloSummary(
        simulations,
        _quantile([p.final_r for p in paths],0.50),
        _quantile([p.final_r for p in paths],0.05),
        _quantile([p.max_drawdown_r for p in paths],0.95),
        int(_quantile([p.max_losing_streak for p in paths],0.95)),
    )
