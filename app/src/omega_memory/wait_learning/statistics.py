from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable
from omega_memory.domain.models import WaitEvaluation, WaitOutcomeClass

@dataclass(frozen=True, slots=True)
class FilterStats:
    reason_code: str
    total_waits: int
    evaluable_waits: int
    avoided_bad: int
    missed_good: int
    neutral: int
    incomplete: int
    avoided_bad_rate: Decimal
    missed_good_rate: Decimal
    utility_score: Decimal
    reason_codes: tuple[str, ...]

def aggregate_filter_stats(
    evaluations: Iterable[WaitEvaluation],
    reason_code: str,
    *,
    avoided_bad_weight: Decimal = Decimal("1"),
    missed_good_weight: Decimal = Decimal("1"),
    min_samples: int = 30,
) -> FilterStats:
    rows = [e for e in evaluations if reason_code in e.reason_codes]
    avoided = sum(e.outcome_class is WaitOutcomeClass.AVOIDED_BAD for e in rows)
    missed = sum(e.outcome_class is WaitOutcomeClass.MISSED_GOOD for e in rows)
    neutral = sum(e.outcome_class is WaitOutcomeClass.NEUTRAL for e in rows)
    incomplete = sum(e.outcome_class in {WaitOutcomeClass.INCOMPLETE,WaitOutcomeClass.UNEVALUABLE} for e in rows)
    evaluable = avoided + missed + neutral
    if evaluable:
        avoided_rate = Decimal(avoided) / Decimal(evaluable)
        missed_rate = Decimal(missed) / Decimal(evaluable)
    else:
        avoided_rate = missed_rate = Decimal("0")
    utility = avoided_rate * avoided_bad_weight - missed_rate * missed_good_weight
    reasons = []
    if evaluable < min_samples:
        reasons.append("MEMORY_FILTER_SAMPLE_TOO_SMALL")
    return FilterStats(
        reason_code,len(rows),evaluable,avoided,missed,neutral,incomplete,
        avoided_rate,missed_rate,utility,tuple(reasons)
    )

def drift_detected(
    historical: FilterStats,
    recent: FilterStats,
    *,
    utility_delta_threshold: Decimal = Decimal("0.25"),
    min_recent_samples: int = 20,
) -> bool:
    if recent.evaluable_waits < min_recent_samples:
        return False
    return abs(recent.utility_score - historical.utility_score) >= utility_delta_threshold
