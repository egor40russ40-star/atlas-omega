from __future__ import annotations
from decimal import Decimal
from omega_strategy.domain.models import ScoreComponents, StrategyScore, StrategyProposal

WEIGHTS = {
    "setup_quality": Decimal("0.18"),
    "regime_fit": Decimal("0.12"),
    "timeframe_alignment": Decimal("0.12"),
    "orderflow_support": Decimal("0.10"),
    "level_quality": Decimal("0.10"),
    "context_support": Decimal("0.08"),
    "historical_quality": Decimal("0.12"),
    "execution_readiness": Decimal("0.08"),
    "data_quality": Decimal("0.10"),
}

def _clamp(v: Decimal) -> Decimal:
    return max(Decimal("0"), min(v, Decimal("1")))

def score_components(c: ScoreComponents) -> Decimal:
    positive = (
        _clamp(c.setup_quality) * WEIGHTS["setup_quality"]
        + _clamp(c.regime_fit) * WEIGHTS["regime_fit"]
        + _clamp(c.timeframe_alignment) * WEIGHTS["timeframe_alignment"]
        + _clamp(c.orderflow_support) * WEIGHTS["orderflow_support"]
        + _clamp(c.level_quality) * WEIGHTS["level_quality"]
        + _clamp(c.context_support) * WEIGHTS["context_support"]
        + _clamp(c.historical_quality) * WEIGHTS["historical_quality"]
        + _clamp(c.execution_readiness) * WEIGHTS["execution_readiness"]
        + _clamp(c.data_quality) * WEIGHTS["data_quality"]
    )
    penalty = _clamp(c.uncertainty_penalty) * Decimal("0.35")
    return _clamp(positive - penalty)

def score_proposal(p: StrategyProposal) -> StrategyScore:
    final = score_components(p.score_components)
    reasons = []
    if final < Decimal("0.65") and p.proposal_class.value == "ENTRY":
        reasons.append("STRAT_SCORE_TOO_LOW")
    return StrategyScore(p.proposal_id, final, tuple(reasons))
