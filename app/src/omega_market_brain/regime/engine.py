from __future__ import annotations
from decimal import Decimal
from omega_market_brain.domain.models import (
    RegimeProbabilities, LiquidityState
)

def _clamp(v: Decimal) -> Decimal:
    return max(Decimal("0"), min(v, Decimal("1")))

def regime_probabilities(
    *,
    direction_score: Decimal,
    conflict_score: Decimal,
    compression_score: Decimal,
    breakout_score_up: Decimal,
    breakout_score_down: Decimal,
    volatility_score: Decimal,
    liquidity_state: LiquidityState,
) -> RegimeProbabilities:
    directional_confidence = _clamp(Decimal("1") - conflict_score)
    trend_up = _clamp(max(direction_score, Decimal("0")) * directional_confidence)
    trend_down = _clamp(max(-direction_score, Decimal("0")) * directional_confidence)
    compression = _clamp(compression_score)
    breakout_up = _clamp(breakout_score_up)
    breakout_down = _clamp(breakout_score_down)
    high_volatility = _clamp(volatility_score)
    low_liquidity = Decimal("1") if liquidity_state is LiquidityState.POOR else (
        Decimal("0.65") if liquidity_state is LiquidityState.THIN else Decimal("0")
    )
    transition = _clamp(conflict_score * Decimal("0.8"))
    directional_strength = max(abs(direction_score), breakout_up, breakout_down)
    range_p = _clamp(
        (Decimal("1") - directional_strength)
        * (Decimal("1") - compression * Decimal("0.7"))
        * (Decimal("1") - high_volatility * Decimal("0.4"))
    )
    return RegimeProbabilities(
        trend_up=trend_up,
        trend_down=trend_down,
        range=range_p,
        compression=compression,
        breakout_up=breakout_up,
        breakout_down=breakout_down,
        transition=transition,
        high_volatility=high_volatility,
        low_liquidity=low_liquidity,
    )

def dominant_regime(regimes: RegimeProbabilities, minimum_probability: Decimal = Decimal("0.45")) -> str | None:
    values = {
        "TREND_UP": regimes.trend_up,
        "TREND_DOWN": regimes.trend_down,
        "RANGE": regimes.range,
        "COMPRESSION": regimes.compression,
        "BREAKOUT_UP": regimes.breakout_up,
        "BREAKOUT_DOWN": regimes.breakout_down,
        "TRANSITION": regimes.transition,
        "HIGH_VOLATILITY": regimes.high_volatility,
        "LOW_LIQUIDITY": regimes.low_liquidity,
    }
    name, value = max(values.items(), key=lambda kv: kv[1])
    return name if value >= minimum_probability else None

def normalized_distribution(regimes: RegimeProbabilities) -> dict[str, Decimal]:
    values = {
        "TREND_UP": regimes.trend_up,
        "TREND_DOWN": regimes.trend_down,
        "RANGE": regimes.range,
        "COMPRESSION": regimes.compression,
        "BREAKOUT_UP": regimes.breakout_up,
        "BREAKOUT_DOWN": regimes.breakout_down,
        "TRANSITION": regimes.transition,
        "HIGH_VOLATILITY": regimes.high_volatility,
        "LOW_LIQUIDITY": regimes.low_liquidity,
    }
    total = sum(values.values(), Decimal("0"))
    if total <= 0:
        n = Decimal(len(values))
        return {k: Decimal("1") / n for k in values}
    return {k: v / total for k, v in values.items()}
