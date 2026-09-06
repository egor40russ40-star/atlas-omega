from __future__ import annotations
from dataclasses import dataclass
from omega_execution.domain.models import OrderState, ExecutionRequest

@dataclass(frozen=True, slots=True)
class UnknownOutcomeResolution:
    state: OrderState
    broker_order_id: str | None
    reason_codes: tuple[str, ...]

def resolve_unknown_outcome(request: ExecutionRequest, broker_port) -> UnknownOutcomeResolution:
    # First preference: deterministic client tag / idempotency key.
    found = broker_port.find_order_by_client_tag(
        request.broker_account_id,
        request.idempotency_key,
    )
    if found is not None:
        state = found.state.upper()
        if state in {"FILLED"}:
            return UnknownOutcomeResolution(OrderState.FILLED, found.broker_order_id, ())
        if found.filled_quantity > 0:
            return UnknownOutcomeResolution(OrderState.PARTIALLY_FILLED, found.broker_order_id, ("EXEC_PARTIAL_FILL",))
        return UnknownOutcomeResolution(OrderState.ACCEPTED, found.broker_order_id, ())

    # If not found by tag, inspect active/recent orders.
    candidates = list(broker_port.get_active_orders(request.broker_account_id)) + \
                 list(broker_port.get_recent_orders(request.broker_account_id))

    for o in candidates:
        if (
            o.instrument_id == request.instrument_id
            and o.side == request.side
            and o.requested_quantity == request.quantity
            and o.client_tag == request.idempotency_key
        ):
            return UnknownOutcomeResolution(OrderState.ACCEPTED, o.broker_order_id, ())

    # Absence in both active and recent order lists permits only "safe retry allowed",
    # never an automatic immediate retry inside this resolver.
    return UnknownOutcomeResolution(
        OrderState.SAFE_RETRY_ALLOWED,
        None,
        ("EXEC_SAFE_RETRY_ALLOWED",)
    )
