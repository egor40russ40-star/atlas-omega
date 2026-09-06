from __future__ import annotations
from decimal import Decimal

def correlated_risk_exceeded(
    *,
    existing_group_risk_rub: Decimal,
    added_risk_rub: Decimal,
    correlation: Decimal,
    group_risk_limit_rub: Decimal | None,
    correlation_threshold: Decimal = Decimal("0.85"),
) -> bool:
    if group_risk_limit_rub is None:
        return False
    if abs(correlation) < correlation_threshold:
        return False
    return existing_group_risk_rub + added_risk_rub > group_risk_limit_rub
