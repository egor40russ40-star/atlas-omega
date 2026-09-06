from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class IdeaLimits:
    per_strategy_daily: int | None = None
    per_instrument_daily: int | None = None
    total_daily: int | None = None

def idea_limit_reasons(
    *,
    used_strategy: int,
    used_instrument: int,
    used_total: int,
    limits: IdeaLimits,
) -> list[str]:
    reasons = []
    if limits.per_strategy_daily is not None and used_strategy >= limits.per_strategy_daily:
        reasons.append("STRAT_IDEA_LIMIT_REACHED")
    if limits.per_instrument_daily is not None and used_instrument >= limits.per_instrument_daily:
        reasons.append("STRAT_IDEA_LIMIT_REACHED")
    if limits.total_daily is not None and used_total >= limits.total_daily:
        reasons.append("STRAT_IDEA_LIMIT_REACHED")
    return sorted(set(reasons))
