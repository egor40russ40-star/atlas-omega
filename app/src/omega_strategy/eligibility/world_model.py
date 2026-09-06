from __future__ import annotations

def eligibility_reasons(world_model, *, family: str) -> list[str]:
    reasons = []
    if getattr(world_model, "no_trade", False):
        reasons.append("STRAT_WORLD_MODEL_NO_TRADE")
    if not getattr(world_model, "execution_ready", False):
        reasons.append("STRAT_EXECUTION_NOT_READY")
    from omega_strategy.eligibility.regime import regime_eligible
    if not regime_eligible(family, getattr(world_model, "dominant_regime", None)):
        reasons.append("STRAT_NOT_ELIGIBLE_FOR_REGIME")
    return sorted(set(reasons))
