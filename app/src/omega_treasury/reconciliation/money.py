from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True, slots=True)
class MoneyReconciliation:
    expected_cash: Decimal
    broker_cash: Decimal
    delta: Decimal
    status: str
    reason_codes: tuple[str, ...]

def reconcile_cash(expected_cash: Decimal, broker_cash: Decimal, tolerance: Decimal = Decimal("0.01")) -> MoneyReconciliation:
    delta = broker_cash - expected_cash
    if abs(delta) <= tolerance:
        return MoneyReconciliation(expected_cash, broker_cash, delta, "OK", ())
    # Treasury does not invent the reason for the delta.
    severity = "BLOCKING" if delta < 0 else "WARNING"
    return MoneyReconciliation(
        expected_cash, broker_cash, delta, severity,
        ("TREASURY_UNCLASSIFIED_BALANCE_CHANGE",)
    )
