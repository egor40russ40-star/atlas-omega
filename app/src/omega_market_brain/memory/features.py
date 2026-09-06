from __future__ import annotations
from decimal import Decimal
from typing import Mapping
from omega_market_brain.domain.models import (
    TimeframeState, OrderFlowState, ContextGraphState,
    RegimeProbabilities
)

TF_ORDER = ("1m","5m","15m","1h","4h","1D")

def build_feature_vector(
    *,
    timeframes: Mapping[str, TimeframeState],
    price: Decimal,
    orderflow: OrderFlowState | None,
    context: ContextGraphState | None,
    regimes: RegimeProbabilities,
    timeframe_conflict: Decimal,
    uncertainty_score: Decimal,
) -> dict[str, float]:
    f: dict[str, float] = {}
    for tf in TF_ORDER:
        s = timeframes.get(tf)
        if s is None:
            f[f"tf_{tf}_present"] = 0.0
            continue
        f[f"tf_{tf}_present"] = 1.0
        f[f"tf_{tf}_direction"] = float(s.direction_score)
        f[f"tf_{tf}_confidence"] = float(s.confidence)
        f[f"tf_{tf}_quality"] = float(s.data_quality_score)
        f[f"tf_{tf}_atr_pct"] = float(s.atr_pct or Decimal("0"))
        f[f"tf_{tf}_volume_ratio"] = float(s.volume_ratio or Decimal("0"))
        if s.support is not None and price != 0:
            f[f"tf_{tf}_dist_support_pct"] = float((price - s.support.price) / price)
        if s.resistance is not None and price != 0:
            f[f"tf_{tf}_dist_resistance_pct"] = float((s.resistance.price - price) / price)

    if orderflow is not None:
        f["of_spread_pct"] = float(orderflow.spread_pct)
        f["of_imbalance"] = float(orderflow.bid_ask_imbalance)
        f["of_pressure"] = float(orderflow.pressure_score)
        f["of_sweep_up"] = 1.0 if orderflow.sweep_up else 0.0
        f["of_sweep_down"] = 1.0 if orderflow.sweep_down else 0.0

    if context is not None:
        f["ctx_aggregate"] = float(context.aggregate_score)
        f["ctx_conflict"] = float(context.conflict_score)
        f["ctx_freshness"] = float(context.freshness_score)

    f.update({
        "regime_trend_up": float(regimes.trend_up),
        "regime_trend_down": float(regimes.trend_down),
        "regime_range": float(regimes.range),
        "regime_compression": float(regimes.compression),
        "regime_breakout_up": float(regimes.breakout_up),
        "regime_breakout_down": float(regimes.breakout_down),
        "regime_transition": float(regimes.transition),
        "regime_high_volatility": float(regimes.high_volatility),
        "regime_low_liquidity": float(regimes.low_liquidity),
        "timeframe_conflict": float(timeframe_conflict),
        "uncertainty": float(uncertainty_score),
    })
    return f
