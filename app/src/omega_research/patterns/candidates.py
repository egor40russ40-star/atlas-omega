from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

@dataclass(frozen=True, slots=True)
class PatternCandidate:
    name: str
    support_count: int
    positive_rate: Decimal
    baseline_rate: Decimal
    lift: Decimal
    stable_across_regimes: bool
    reason_codes: tuple[str,...]

def build_binary_pattern_candidate(
    *,
    name: str,
    pattern_outcomes: Iterable[bool],
    baseline_rate: Decimal,
    stable_across_regimes: bool,
    min_support: int = 30,
) -> PatternCandidate:
    xs=list(pattern_outcomes)
    support=len(xs)
    pos=Decimal(sum(xs))/Decimal(support) if support else Decimal("0")
    lift=pos-baseline_rate
    reasons=[]
    if support<min_support:
        reasons.append("RESEARCH_OVERFIT_SAMPLE_TOO_SMALL")
    return PatternCandidate(name,support,pos,baseline_rate,lift,stable_across_regimes,tuple(reasons))
