from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from omega_execution.domain.models import BrokerOrderSnapshot, BrokerPositionSnapshot
from omega_execution.reconciliation.engine import (
    ReconciliationReport, reconcile_orders, reconcile_positions
)

@dataclass(frozen=True, slots=True)
class RecoveryResult:
    status: str
    order_report: ReconciliationReport
    position_report: ReconciliationReport
    ready_for_safe_state: bool

def rebuild_from_broker_truth(
    *,
    local_orders: Iterable[BrokerOrderSnapshot],
    broker_orders: Iterable[BrokerOrderSnapshot],
    local_positions: Iterable[BrokerPositionSnapshot],
    broker_positions: Iterable[BrokerPositionSnapshot],
) -> RecoveryResult:
    order_report = reconcile_orders(local_orders, broker_orders)
    position_report = reconcile_positions(local_positions, broker_positions)
    statuses = {order_report.status, position_report.status}
    if "CRITICAL" in statuses:
        status = "CRITICAL"
    elif "BLOCKING" in statuses:
        status = "BLOCKING"
    elif "WARNING" in statuses:
        status = "WARNING"
    else:
        status = "OK"

    return RecoveryResult(
        status=status,
        order_report=order_report,
        position_report=position_report,
        ready_for_safe_state=(status in {"OK","WARNING"}),
    )
