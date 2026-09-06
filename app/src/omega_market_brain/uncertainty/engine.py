from __future__ import annotations
from decimal import Decimal
from omega_market_brain.domain.models import (
    UncertaintyLevel, UncertaintyState, LiquidityState
)

def classify_uncertainty(score: Decimal) -> UncertaintyLevel:
    if score >= Decimal("0.82"):
        return UncertaintyLevel.EXTREME
    if score >= Decimal("0.65"):
        return UncertaintyLevel.HIGH
    if score >= Decimal("0.35"):
        return UncertaintyLevel.MEDIUM
    return UncertaintyLevel.LOW

def calculate_uncertainty(
    *,
    regime_entropy: Decimal,
    timeframe_conflict: Decimal,
    data_quality_score: Decimal,
    context_conflict: Decimal,
    context_freshness: Decimal,
    liquidity_state: LiquidityState,
    levels_ambiguity: Decimal,
    execution_not_ready: bool,
) -> UncertaintyState:
    low_quality = Decimal("1") - max(Decimal("0"), min(data_quality_score, Decimal("1")))
    stale_context = Decimal("1") - max(Decimal("0"), min(context_freshness, Decimal("1")))
    liquidity_penalty = {
        LiquidityState.GOOD: Decimal("0"),
        LiquidityState.NORMAL: Decimal("0.1"),
        LiquidityState.THIN: Decimal("0.6"),
        LiquidityState.POOR: Decimal("1"),
        LiquidityState.UNKNOWN: Decimal("0.5"),
    }[liquidity_state]
    execution_penalty = Decimal("0.7") if execution_not_ready else Decimal("0")

    score = (
        regime_entropy * Decimal("0.22")
        + timeframe_conflict * Decimal("0.20")
        + low_quality * Decimal("0.20")
        + context_conflict * Decimal("0.10")
        + stale_context * Decimal("0.08")
        + liquidity_penalty * Decimal("0.08")
        + levels_ambiguity * Decimal("0.07")
        + execution_penalty * Decimal("0.05")
    )
    score = max(Decimal("0"), min(score, Decimal("1")))
    level = classify_uncertainty(score)
    reasons = []
    if timeframe_conflict >= Decimal("0.55"):
        reasons.append("BRAIN_TIMEFRAME_CONFLICT_HIGH")
    if data_quality_score < Decimal("0.80"):
        reasons.append("BRAIN_DATA_QUALITY_LOW")
    if regime_entropy >= Decimal("0.82"):
        reasons.append("BRAIN_REGIME_AMBIGUOUS")
    if liquidity_penalty >= Decimal("0.6"):
        reasons.append("BRAIN_LOW_LIQUIDITY")
    if levels_ambiguity >= Decimal("0.6"):
        reasons.append("BRAIN_LEVELS_AMBIGUOUS")
    if execution_not_ready:
        reasons.append("BRAIN_EXECUTION_TF_NOT_READY")
    if level is UncertaintyLevel.HIGH:
        reasons.append("BRAIN_UNCERTAINTY_HIGH")
    if level is UncertaintyLevel.EXTREME:
        reasons.append("BRAIN_UNCERTAINTY_EXTREME")
    return UncertaintyState(score, level, tuple(sorted(set(reasons))))
