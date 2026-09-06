from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import MutableMapping, Optional

from omega_execution.domain.models import (
    ExecutionRequest, BrokerSubmitStatus, BrokerSubmitResult, OrderState
)
from omega_execution.domain.state_machine import require_transition

@dataclass
class ExecutionRecord:
    request: ExecutionRequest
    state: OrderState
    broker_order_id: Optional[str] = None
    last_message: Optional[str] = None

class ExecutionEngine:
    def __init__(self, broker_port) -> None:
        self.broker = broker_port
        self._records_by_key: MutableMapping[str, ExecutionRecord] = {}

    def existing(self, idempotency_key: str) -> ExecutionRecord | None:
        return self._records_by_key.get(idempotency_key)

    def submit(self, request: ExecutionRequest, *, approvals_ok: bool, broker_state_fresh: bool) -> ExecutionRecord:
        existing = self.existing(request.idempotency_key)
        if existing is not None:
            return existing

        now = datetime.now(timezone.utc)
        if request.valid_until <= now:
            rec = ExecutionRecord(request, OrderState.REJECTED, last_message="EXEC_APPROVAL_EXPIRED")
            self._records_by_key[request.idempotency_key] = rec
            return rec
        if not approvals_ok:
            rec = ExecutionRecord(request, OrderState.REJECTED, last_message="EXEC_APPROVAL_MISSING")
            self._records_by_key[request.idempotency_key] = rec
            return rec
        if not broker_state_fresh:
            rec = ExecutionRecord(request, OrderState.REJECTED, last_message="EXEC_STALE_BROKER_STATE")
            self._records_by_key[request.idempotency_key] = rec
            return rec

        rec = ExecutionRecord(request, OrderState.VALIDATED)
        self._records_by_key[request.idempotency_key] = rec

        require_transition(rec.state, OrderState.SUBMITTING)
        rec.state = OrderState.SUBMITTING

        result: BrokerSubmitResult = self.broker.submit_order(request)

        if result.status is BrokerSubmitStatus.ACCEPTED:
            require_transition(rec.state, OrderState.ACCEPTED)
            rec.state = OrderState.ACCEPTED
            rec.broker_order_id = result.broker_order_id
            rec.last_message = result.message
            return rec

        if result.status is BrokerSubmitStatus.REJECTED:
            require_transition(rec.state, OrderState.REJECTED)
            rec.state = OrderState.REJECTED
            rec.last_message = result.message
            return rec

        # Anything ambiguous after submit is UNKNOWN_OUTCOME.
        require_transition(rec.state, OrderState.UNKNOWN_OUTCOME)
        rec.state = OrderState.UNKNOWN_OUTCOME
        rec.last_message = "EXEC_UNKNOWN_OUTCOME"
        return rec
