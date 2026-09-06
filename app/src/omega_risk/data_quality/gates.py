from __future__ import annotations
from decimal import Decimal

def data_quality_reasons(
    *,
    market_data_age_seconds: Decimal,
    broker_state_age_seconds: Decimal,
    data_quality_score: Decimal,
    max_market_data_age_seconds: Decimal,
    max_broker_state_age_seconds: Decimal,
    min_data_quality_score: Decimal,
    reconciliation_status: str,
) -> list[str]:
    reasons: list[str] = []
    if market_data_age_seconds > max_market_data_age_seconds:
        reasons.append("RISK_STALE_MARKET_DATA")
    if broker_state_age_seconds > max_broker_state_age_seconds:
        reasons.append("RISK_STALE_BROKER_STATE")
    if data_quality_score < min_data_quality_score:
        reasons.append("RISK_DATA_QUALITY_LOW")
    if reconciliation_status in {"BLOCKING", "CRITICAL"}:
        reasons.append("RISK_RECONCILIATION_BLOCK")
    return sorted(set(reasons))
