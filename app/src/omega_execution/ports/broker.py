from __future__ import annotations
from typing import Protocol, Iterable
from omega_execution.domain.models import (
    ExecutionRequest, BrokerSubmitResult,
    BrokerOrderSnapshot, BrokerPositionSnapshot
)

class BrokerExecutionPort(Protocol):
    def submit_order(self, request: ExecutionRequest) -> BrokerSubmitResult:
        ...

    def cancel_order(self, broker_account_id: str, broker_order_id: str) -> BrokerSubmitResult:
        ...

    def get_active_orders(self, broker_account_id: str) -> Iterable[BrokerOrderSnapshot]:
        ...

    def get_recent_orders(self, broker_account_id: str) -> Iterable[BrokerOrderSnapshot]:
        ...

    def get_positions(self, broker_account_id: str) -> Iterable[BrokerPositionSnapshot]:
        ...

    def find_order_by_client_tag(self, broker_account_id: str, client_tag: str) -> BrokerOrderSnapshot | None:
        ...
