from __future__ import annotations
from decimal import Decimal
from typing import Iterable
from omega_twin.domain.models import TradeResult, ValidationMetrics

def max_consecutive_losses(trades: list[TradeResult]) -> int:
    best=cur=0
    for t in trades:
        if t.pnl_r_after_costs < 0:
            cur+=1; best=max(best,cur)
        else:
            cur=0
    return best

def max_drawdown_r(trades: list[TradeResult]) -> Decimal:
    equity=Decimal("0")
    high=Decimal("0")
    dd=Decimal("0")
    for t in trades:
        equity += t.pnl_r_after_costs
        high=max(high,equity)
        dd=max(dd,high-equity)
    return dd

def compute_metrics(trades: Iterable[TradeResult]) -> ValidationMetrics:
    ts=list(trades)
    if not ts:
        return ValidationMetrics(
            0,Decimal("0"),Decimal("0"),Decimal("0"),None,
            Decimal("0"),0,Decimal("0"),Decimal("0"),0
        )
    wins=sum(t.pnl_r_after_costs>0 for t in ts)
    expectancy=sum((t.pnl_r for t in ts),Decimal("0"))/Decimal(len(ts))
    expectancy_after=sum((t.pnl_r_after_costs for t in ts),Decimal("0"))/Decimal(len(ts))
    gross_profit=sum((t.pnl_r_after_costs for t in ts if t.pnl_r_after_costs>0),Decimal("0"))
    gross_loss=-sum((t.pnl_r_after_costs for t in ts if t.pnl_r_after_costs<0),Decimal("0"))
    pf=None if gross_loss==0 else gross_profit/gross_loss
    return ValidationMetrics(
        len(ts),
        Decimal(wins)/Decimal(len(ts)),
        expectancy,
        expectancy_after,
        pf,
        max_drawdown_r(ts),
        max_consecutive_losses(ts),
        sum((t.commission for t in ts),Decimal("0")),
        sum((t.slippage_cost for t in ts),Decimal("0")),
        sum(t.safety_violations for t in ts),
    )
