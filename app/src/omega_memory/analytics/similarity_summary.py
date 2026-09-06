from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping
from uuid import UUID
from omega_memory.domain.models import SimilarObservation, ObservationOutcome

@dataclass(frozen=True, slots=True)
class SimilarityOutcomeSummary:
    support_count: int
    positive_rate: Decimal | None
    negative_rate: Decimal | None
    median_return_pct: Decimal | None

def summarize_neighbours(
    neighbours: tuple[SimilarObservation,...],
    outcomes: Mapping[UUID,ObservationOutcome],
    *,
    horizon_seconds: int,
) -> SimilarityOutcomeSummary:
    returns=[]
    for n in neighbours:
        o=outcomes.get(n.observation_id)
        if o is None:
            continue
        h=o.horizons.get(horizon_seconds)
        if h is None or not h.path_complete or h.return_pct is None:
            continue
        returns.append(h.return_pct)
    if not returns:
        return SimilarityOutcomeSummary(0,None,None,None)
    positives=sum(r>0 for r in returns)
    negatives=sum(r<0 for r in returns)
    xs=sorted(returns)
    mid=len(xs)//2
    median=xs[mid] if len(xs)%2 else (xs[mid-1]+xs[mid])/Decimal("2")
    return SimilarityOutcomeSummary(
        len(returns),
        Decimal(positives)/Decimal(len(returns)),
        Decimal(negatives)/Decimal(len(returns)),
        median
    )
