from __future__ import annotations
from datetime import datetime, timedelta
from omega_strategy.domain.models import ProposalClass, StrategyContext

def cooldown_reasons(
    context: StrategyContext,
    *,
    proposal_class: ProposalClass,
    after_stop_seconds: int,
    after_entry_seconds: int,
) -> list[str]:
    if proposal_class in {ProposalClass.PROTECTIVE, ProposalClass.EXIT}:
        return []
    reasons = []
    now = context.now
    if context.last_stop_at is not None and now < context.last_stop_at + timedelta(seconds=after_stop_seconds):
        reasons.append("STRAT_COOLDOWN_ACTIVE")
    if context.last_entry_at is not None and now < context.last_entry_at + timedelta(seconds=after_entry_seconds):
        reasons.append("STRAT_COOLDOWN_ACTIVE")
    return sorted(set(reasons))
