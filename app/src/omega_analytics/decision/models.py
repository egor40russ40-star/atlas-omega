from dataclasses import dataclass


@dataclass
class DecisionResult:
    action: str
    score: int

    reasons: list[str]

    confidence: str