from __future__ import annotations
from decimal import Decimal
from omega_execution.domain.models import OrderState

def derive_order_state(requested: Decimal, filled: Decimal, broker_state: str) -> OrderState:
    if filled >= requested and requested > 0:
        return OrderState.FILLED
    if filled > 0:
        return OrderState.PARTIALLY_FILLED
    state = broker_state.upper()
    if state in {"CANCELLED","CANCELED"}:
        return OrderState.CANCELLED
    if state == "REJECTED":
        return OrderState.REJECTED
    if state == "EXPIRED":
        return OrderState.EXPIRED
    if state in {"ACCEPTED","NEW","ACTIVE"}:
        return OrderState.ACCEPTED
    return OrderState.UNKNOWN_OUTCOME

def remaining_quantity(requested: Decimal, filled: Decimal) -> Decimal:
    r = requested - filled
    return max(r, Decimal("0"))
