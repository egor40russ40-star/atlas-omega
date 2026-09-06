from __future__ import annotations
from omega_research.domain.models import MutableParameter

FORBIDDEN_PARAMETER_TOKENS = (
    "kill_switch",
    "safety",
    "fail_closed",
    "broker_token",
    "idempotency",
    "reconciliation_required",
    "borrowed_long_limit_rub",
    "borrowed_hedge_limit_rub",
)

def parameter_is_protected(name: str) -> bool:
    low=name.lower()
    return any(tok in low for tok in FORBIDDEN_PARAMETER_TOKENS)

def validate_mutable_parameter(p: MutableParameter) -> None:
    if parameter_is_protected(p.name):
        raise ValueError("RESEARCH_GENETIC_FORBIDDEN_PARAMETER")
    if not p.research_only:
        raise ValueError("RESEARCH_LIVE_WRITE_FORBIDDEN")
    if not (p.minimum <= p.baseline <= p.maximum):
        raise ValueError("RESEARCH_MUTATION_OUT_OF_BOUNDS")
