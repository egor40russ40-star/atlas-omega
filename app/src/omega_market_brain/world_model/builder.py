from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Mapping
from omega_market_brain.domain.models import (
    TimeframeState, OrderFlowState, ContextGraphState, WorldModelSnapshot,
    LiquidityState, UncertaintyLevel
)
from omega_market_brain.timeframes.conflict import weighted_bias, conflict_score
from omega_market_brain.regime.engine import regime_probabilities, dominant_regime, normalized_distribution
from omega_market_brain.regime.entropy import normalized_entropy
from omega_market_brain.uncertainty.engine import calculate_uncertainty
from omega_market_brain.quality.propagation import aggregate_quality
from omega_market_brain.memory.features import build_feature_vector
from omega_market_brain.levels.quality import ambiguity_score

def _strategic_bias(states: Mapping[str, TimeframeState]) -> str:
    strategic = {k:v for k,v in states.items() if k in {"1D","4h","1h"}}
    b = weighted_bias(strategic or states)
    if b >= Decimal("0.25"):
        return "LONG"
    if b <= Decimal("-0.25"):
        return "SHORT"
    return "NEUTRAL"

def _execution_ready(states: Mapping[str, TimeframeState], strategic_bias: str) -> bool:
    one = states.get("1m")
    five = states.get("5m")
    if one is None:
        return False
    if one.data_quality_score < Decimal("0.80") or one.confidence < Decimal("0.45"):
        return False
    if strategic_bias == "LONG" and one.direction_score < Decimal("-0.20"):
        return False
    if strategic_bias == "SHORT" and one.direction_score > Decimal("0.20"):
        return False
    if five is not None and five.data_quality_score < Decimal("0.75"):
        return False
    return True

def build_world_model(
    *,
    instrument_id: str,
    captured_at: datetime,
    price: Decimal,
    timeframes: Mapping[str, TimeframeState],
    orderflow: OrderFlowState | None,
    context: ContextGraphState | None,
    compression_score_value: Decimal,
    breakout_score_up: Decimal,
    breakout_score_down: Decimal,
    volatility_score: Decimal,
    minimum_dominant_probability: Decimal = Decimal("0.45"),
) -> WorldModelSnapshot:
    tf_conflict = conflict_score(timeframes)
    bias_score = weighted_bias(timeframes)
    liquidity = orderflow.liquidity_state if orderflow else LiquidityState.UNKNOWN

    regimes = regime_probabilities(
        direction_score=bias_score,
        conflict_score=tf_conflict,
        compression_score=compression_score_value,
        breakout_score_up=breakout_score_up,
        breakout_score_down=breakout_score_down,
        volatility_score=volatility_score,
        liquidity_state=liquidity,
    )
    dom = dominant_regime(regimes, minimum_dominant_probability)
    entropy = normalized_entropy(normalized_distribution(regimes))
    strategic_bias = _strategic_bias(timeframes)
    execution_ready = _execution_ready(timeframes, strategic_bias)

    supports = [s.support for s in timeframes.values() if s.support is not None]
    resistances = [s.resistance for s in timeframes.values() if s.resistance is not None]
    nearest_support = max(supports, key=lambda x: x.price) if supports else None
    nearest_resistance = min(resistances, key=lambda x: x.price) if resistances else None
    atrs = [s.atr for s in timeframes.values() if s.atr is not None]
    ref_atr = sum(atrs, Decimal("0")) / Decimal(len(atrs)) if atrs else None
    level_ambiguity = ambiguity_score(nearest_support, nearest_resistance, atr=ref_atr)

    quality = aggregate_quality(timeframes)
    ctx_conflict = context.conflict_score if context else Decimal("0.5")
    ctx_freshness = context.freshness_score if context else Decimal("0")

    uncertainty = calculate_uncertainty(
        regime_entropy=entropy,
        timeframe_conflict=tf_conflict,
        data_quality_score=quality,
        context_conflict=ctx_conflict,
        context_freshness=ctx_freshness,
        liquidity_state=liquidity,
        levels_ambiguity=level_ambiguity,
        execution_not_ready=not execution_ready,
    )

    reasons = list(uncertainty.reason_codes)
    if context:
        reasons.extend(context.reason_codes)
    if dom is None:
        reasons.append("BRAIN_REGIME_AMBIGUOUS")

    no_trade = (
        uncertainty.level is UncertaintyLevel.EXTREME
        or quality < Decimal("0.80")
    )
    if no_trade:
        reasons.append("BRAIN_NO_TRADE")

    tactical_state = "READY" if execution_ready and not no_trade else "WAIT"
    feature_vector = build_feature_vector(
        timeframes=timeframes,
        price=price,
        orderflow=orderflow,
        context=context,
        regimes=regimes,
        timeframe_conflict=tf_conflict,
        uncertainty_score=uncertainty.score,
    )

    return WorldModelSnapshot(
        instrument_id=instrument_id,
        captured_at=captured_at,
        price=price,
        timeframes=timeframes,
        orderflow=orderflow,
        context=context,
        regimes=regimes,
        dominant_regime=dom,
        timeframe_conflict_score=tf_conflict,
        uncertainty=uncertainty,
        strategic_bias=strategic_bias,
        tactical_state=tactical_state,
        execution_ready=execution_ready,
        no_trade=no_trade,
        reason_codes=tuple(sorted(set(reasons))),
        feature_vector=feature_vector,
    )
