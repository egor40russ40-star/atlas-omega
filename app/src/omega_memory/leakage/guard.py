from __future__ import annotations
from datetime import datetime
from typing import Mapping

DEFAULT_FORBIDDEN_TOKENS = (
    "outcome","future","mfe","mae","label",
    "forward_return","pnl_after","realized_after"
)

def forbidden_feature_names(
    vector: Mapping[str,float],
    *,
    forbidden_tokens=DEFAULT_FORBIDDEN_TOKENS,
) -> list[str]:
    bad=[]
    for name in vector:
        low=name.lower()
        if any(tok in low for tok in forbidden_tokens):
            bad.append(name)
    return sorted(bad)

def validate_feature_vector(vector: Mapping[str,float]) -> None:
    bad=forbidden_feature_names(vector)
    if bad:
        raise ValueError(f"MEMORY_LEAKAGE_FORBIDDEN_FEATURE:{bad}")

def validate_time_boundary(*, observation_time: datetime, candidate_time: datetime) -> None:
    if candidate_time >= observation_time:
        raise ValueError("MEMORY_FUTURE_NEIGHBOUR_BLOCKED")
