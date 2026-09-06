from __future__ import annotations
from omega_data.domain.models import DataQuality

def score_quality(
    *,
    freshness: float,
    completeness: float,
    sequence_integrity: float,
    source_health: float,
    timestamp_integrity: float,
) -> DataQuality:
    values = {
        "freshness": freshness,
        "completeness": completeness,
        "sequence_integrity": sequence_integrity,
        "source_health": source_health,
        "timestamp_integrity": timestamp_integrity,
    }
    for name, value in values.items():
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must be in [0,1]")

    # Conservative weighted score: freshness + sequence/timestamps matter most for LIVE.
    score = (
        freshness * 0.25
        + completeness * 0.15
        + sequence_integrity * 0.25
        + source_health * 0.15
        + timestamp_integrity * 0.20
    )
    reasons: list[str] = []
    if sequence_integrity < 1.0:
        reasons.append("DATA_SEQUENCE_GAP")
    if timestamp_integrity < 1.0:
        reasons.append("DATA_TIMESTAMP_INVALID")
    if score < 0.80:
        reasons.append("DATA_QUALITY_LOW")

    return DataQuality(
        score=round(score, 6),
        freshness=freshness,
        completeness=completeness,
        sequence_integrity=sequence_integrity,
        source_health=source_health,
        timestamp_integrity=timestamp_integrity,
        reason_codes=tuple(sorted(set(reasons))),
    )
