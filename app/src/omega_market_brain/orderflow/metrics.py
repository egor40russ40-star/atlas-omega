from __future__ import annotations
from decimal import Decimal
from omega_market_brain.domain.models import OrderFlowState, LiquidityState

def imbalance(bid_qty: Decimal, ask_qty: Decimal) -> Decimal:
    total = bid_qty + ask_qty
    if total <= 0:
        return Decimal("0")
    return (bid_qty - ask_qty) / total

def pressure_score(
    *,
    bid_qty: Decimal,
    ask_qty: Decimal,
    aggressive_buy_qty: Decimal = Decimal("0"),
    aggressive_sell_qty: Decimal = Decimal("0"),
) -> Decimal:
    book = imbalance(bid_qty, ask_qty)
    flow_total = aggressive_buy_qty + aggressive_sell_qty
    flow = Decimal("0")
    if flow_total > 0:
        flow = (aggressive_buy_qty - aggressive_sell_qty) / flow_total
    score = book * Decimal("0.6") + flow * Decimal("0.4")
    return max(Decimal("-1"), min(score, Decimal("1")))

def classify_liquidity(spread_pct: Decimal, *, thin_threshold: Decimal, poor_threshold: Decimal) -> LiquidityState:
    if spread_pct >= poor_threshold:
        return LiquidityState.POOR
    if spread_pct >= thin_threshold:
        return LiquidityState.THIN
    if spread_pct <= thin_threshold / Decimal("2"):
        return LiquidityState.GOOD
    return LiquidityState.NORMAL

def make_orderflow_state(
    *,
    spread_pct: Decimal,
    bid_qty: Decimal,
    ask_qty: Decimal,
    aggressive_buy_qty: Decimal = Decimal("0"),
    aggressive_sell_qty: Decimal = Decimal("0"),
    thin_threshold: Decimal = Decimal("0.0015"),
    poor_threshold: Decimal = Decimal("0.0040"),
    absorption_bid: bool = False,
    absorption_ask: bool = False,
    sweep_up: bool = False,
    sweep_down: bool = False,
    confidence: Decimal = Decimal("1"),
) -> OrderFlowState:
    return OrderFlowState(
        spread_pct=spread_pct,
        bid_ask_imbalance=imbalance(bid_qty, ask_qty),
        pressure_score=pressure_score(
            bid_qty=bid_qty, ask_qty=ask_qty,
            aggressive_buy_qty=aggressive_buy_qty,
            aggressive_sell_qty=aggressive_sell_qty,
        ),
        liquidity_state=classify_liquidity(
            spread_pct, thin_threshold=thin_threshold, poor_threshold=poor_threshold
        ),
        absorption_bid=absorption_bid,
        absorption_ask=absorption_ask,
        sweep_up=sweep_up,
        sweep_down=sweep_down,
        confidence=confidence,
    )
