from __future__ import annotations
from .models import OrderState

ALLOWED_TRANSITIONS: dict[OrderState, set[OrderState]] = {
    OrderState.CREATED: {OrderState.VALIDATED, OrderState.REJECTED},
    OrderState.VALIDATED: {OrderState.SUBMITTING, OrderState.REJECTED},
    OrderState.SUBMITTING: {
        OrderState.SUBMITTED, OrderState.ACCEPTED, OrderState.REJECTED,
        OrderState.UNKNOWN_OUTCOME
    },
    OrderState.SUBMITTED: {
        OrderState.ACCEPTED, OrderState.PARTIALLY_FILLED, OrderState.FILLED,
        OrderState.REJECTED, OrderState.UNKNOWN_OUTCOME
    },
    OrderState.ACCEPTED: {
        OrderState.PARTIALLY_FILLED, OrderState.FILLED,
        OrderState.CANCEL_REQUESTED, OrderState.EXPIRED,
        OrderState.UNKNOWN_OUTCOME
    },
    OrderState.PARTIALLY_FILLED: {
        OrderState.PARTIALLY_FILLED, OrderState.FILLED,
        OrderState.CANCEL_REQUESTED, OrderState.UNKNOWN_OUTCOME
    },
    OrderState.CANCEL_REQUESTED: {
        OrderState.CANCELLED, OrderState.PARTIALLY_FILLED,
        OrderState.FILLED, OrderState.UNKNOWN_OUTCOME
    },
    OrderState.UNKNOWN_OUTCOME: {
        OrderState.RECONCILING
    },
    OrderState.RECONCILING: {
        OrderState.ACCEPTED, OrderState.PARTIALLY_FILLED, OrderState.FILLED,
        OrderState.REJECTED, OrderState.SAFE_RETRY_ALLOWED,
        OrderState.RECOVERY_REQUIRED
    },
    OrderState.SAFE_RETRY_ALLOWED: set(),
    OrderState.RECOVERY_REQUIRED: set(),
    OrderState.FILLED: set(),
    OrderState.CANCELLED: set(),
    OrderState.REJECTED: set(),
    OrderState.EXPIRED: set(),
}

def can_transition(old: OrderState, new: OrderState) -> bool:
    return new in ALLOWED_TRANSITIONS[old]

def require_transition(old: OrderState, new: OrderState) -> None:
    if not can_transition(old, new):
        raise ValueError(f"invalid order transition: {old.value} -> {new.value}")
