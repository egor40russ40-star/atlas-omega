from __future__ import annotations
from math import sqrt
from typing import Iterable, Mapping
from omega_memory.domain.models import MarketObservation, SimilarObservation, ObservationMode

def weighted_euclidean(a: Mapping[str,float], b: Mapping[str,float], weights: Mapping[str,float] | None = None) -> float:
    keys=set(a)|set(b)
    total=0.0
    wsum=0.0
    weights=weights or {}
    for k in keys:
        w=float(weights.get(k,1.0))
        total += w*(float(a.get(k,0.0))-float(b.get(k,0.0)))**2
        wsum += w
    return sqrt(total/wsum) if wsum>0 else 0.0

def distance_to_similarity(distance: float) -> float:
    return 1.0/(1.0+max(distance,0.0))

def find_similar(
    query: MarketObservation,
    candidates: Iterable[MarketObservation],
    *,
    k: int = 25,
    weights: Mapping[str,float] | None = None,
    allowed_modes=(ObservationMode.REAL,ObservationMode.SHADOW),
    strict_past_only: bool = True,
) -> tuple[SimilarObservation,...]:
    out=[]
    for c in candidates:
        if c.observation_id == query.observation_id:
            continue
        if c.source_mode not in allowed_modes:
            continue
        if strict_past_only and c.observed_at >= query.observed_at:
            continue
        d=weighted_euclidean(query.feature_vector,c.feature_vector,weights)
        out.append(SimilarObservation(
            c.observation_id,d,distance_to_similarity(d),c.observed_at,c.source_mode
        ))
    out.sort(key=lambda x:x.distance)
    return tuple(out[:k])
