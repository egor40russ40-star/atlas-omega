from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class CalibrationObservation:
    predicted_probability: float
    outcome: int

def probability_bucket(p: float, width: float = 0.05) -> tuple[float, float]:
    if not 0 <= p <= 1:
        raise ValueError("probability must be in [0,1]")
    low = int(p / width) * width
    if p == 1:
        low = 1 - width
    high = min(1.0, low + width)
    return round(low, 10), round(high, 10)

def brier_score(observations: list[CalibrationObservation]) -> float | None:
    if not observations:
        return None
    return sum((o.predicted_probability - o.outcome) ** 2 for o in observations) / len(observations)
