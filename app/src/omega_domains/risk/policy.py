from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Any
from omega_common.decimal import as_decimal, optional_decimal

@dataclass(frozen=True, slots=True)
class RiskBudget:
    trade_risk_rub: Optional[Decimal] = None
    strategy_risk_rub: Optional[Decimal] = None
    instrument_risk_rub: Optional[Decimal] = None
    account_risk_rub: Optional[Decimal] = None
    portfolio_daily_loss_rub: Optional[Decimal] = None
    max_borrowed_long_rub: Optional[Decimal] = None
    max_borrowed_hedge_rub: Optional[Decimal] = None

@dataclass(frozen=True, slots=True)
class RiskContext:
    realized_pnl_rub: Decimal
    unrealized_pnl_rub: Decimal
    borrowed_long_rub: Decimal
    borrowed_hedge_rub: Decimal
    open_risk_rub: Decimal
    kill_switch: bool
    recovery_in_progress: bool
    market_data_fresh: bool
    reconciliation_ok: bool


def hard_block_reasons(ctx: RiskContext, budget: RiskBudget) -> list[str]:
    reasons: list[str] = []
    if ctx.kill_switch: reasons.append("KILL_SWITCH_ACTIVE")
    if ctx.recovery_in_progress: reasons.append("RECOVERY_IN_PROGRESS")
    if not ctx.market_data_fresh: reasons.append("STALE_MARKET_DATA")
    if not ctx.reconciliation_ok: reasons.append("BROKER_STATE_STALE")
    realized=as_decimal(ctx.realized_pnl_rub,field="realized_pnl_rub")
    unrealized=as_decimal(ctx.unrealized_pnl_rub,field="unrealized_pnl_rub")
    borrowed_long=as_decimal(ctx.borrowed_long_rub,field="borrowed_long_rub")
    borrowed_hedge=as_decimal(ctx.borrowed_hedge_rub,field="borrowed_hedge_rub")
    daily=optional_decimal(budget.portfolio_daily_loss_rub,field="portfolio_daily_loss_rub")
    max_long=optional_decimal(budget.max_borrowed_long_rub,field="max_borrowed_long_rub")
    max_hedge=optional_decimal(budget.max_borrowed_hedge_rub,field="max_borrowed_hedge_rub")
    if daily is not None and realized+unrealized <= -abs(daily): reasons.append("DAILY_RISK_LIMIT_REACHED")
    if max_long is not None and borrowed_long > max_long: reasons.append("BORROWED_FUNDS_LIMIT_EXCEEDED")
    if max_hedge is not None and borrowed_hedge > max_hedge: reasons.append("BORROWED_FUNDS_LIMIT_EXCEEDED")
    return sorted(set(reasons))
