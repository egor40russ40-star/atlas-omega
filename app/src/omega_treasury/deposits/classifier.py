from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

KNOWN_EXTERNAL_DEPOSIT_TYPES = {
    "DEPOSIT", "CASH_IN", "BROKER_DEPOSIT"
}
KNOWN_EXTERNAL_WITHDRAWAL_TYPES = {
    "WITHDRAWAL", "CASH_OUT", "BROKER_WITHDRAWAL"
}
KNOWN_INTERNAL_TRANSFER_TYPES = {
    "INTERNAL_TRANSFER", "ACCOUNT_TRANSFER"
}

@dataclass(frozen=True, slots=True)
class BrokerCashOperation:
    broker_operation_id: str
    operation_type: str
    amount: Decimal
    currency: str
    source_account_id: Optional[str] = None
    destination_account_id: Optional[str] = None

def classify_cash_operation(op: BrokerCashOperation) -> str:
    t = op.operation_type.upper().strip()
    if t in KNOWN_EXTERNAL_DEPOSIT_TYPES:
        return "DEPOSIT"
    if t in KNOWN_EXTERNAL_WITHDRAWAL_TYPES:
        return "WITHDRAWAL"
    if t in KNOWN_INTERNAL_TRANSFER_TYPES:
        return "INTERNAL_TRANSFER"
    return "UNCLASSIFIED_BALANCE_CHANGE"
