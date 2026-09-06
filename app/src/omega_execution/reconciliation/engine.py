from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable
from omega_execution.domain.models import BrokerOrderSnapshot, BrokerPositionSnapshot

@dataclass(frozen=True, slots=True)
class ReconciliationIssue:
    severity: str
    reason_code: str
    details: dict

@dataclass(frozen=True, slots=True)
class ReconciliationReport:
    status: str
    issues: tuple[ReconciliationIssue, ...]

def _overall(issues: list[ReconciliationIssue]) -> str:
    severities = {i.severity for i in issues}
    if "CRITICAL" in severities:
        return "CRITICAL"
    if "BLOCKING" in severities:
        return "BLOCKING"
    if "WARNING" in severities:
        return "WARNING"
    return "OK"

def reconcile_orders(
    local_orders: Iterable[BrokerOrderSnapshot],
    broker_orders: Iterable[BrokerOrderSnapshot],
) -> ReconciliationReport:
    local = {o.broker_order_id: o for o in local_orders}
    broker = {o.broker_order_id: o for o in broker_orders}
    issues: list[ReconciliationIssue] = []

    for oid, bo in broker.items():
        if oid not in local:
            issues.append(ReconciliationIssue(
                "CRITICAL",
                "EXEC_UNEXPECTED_BROKER_ORDER",
                {"broker_order_id": oid, "instrument_id": bo.instrument_id}
            ))

    for oid, lo in local.items():
        if oid not in broker and lo.state.upper() not in {"FILLED","CANCELLED","CANCELED","REJECTED","EXPIRED"}:
            issues.append(ReconciliationIssue(
                "BLOCKING",
                "EXEC_BROKER_ORDER_NOT_FOUND",
                {"broker_order_id": oid, "instrument_id": lo.instrument_id}
            ))

    for oid in local.keys() & broker.keys():
        lo, bo = local[oid], broker[oid]
        if lo.filled_quantity != bo.filled_quantity:
            issues.append(ReconciliationIssue(
                "BLOCKING",
                "EXEC_PARTIAL_FILL",
                {
                    "broker_order_id": oid,
                    "local_filled": str(lo.filled_quantity),
                    "broker_filled": str(bo.filled_quantity),
                }
            ))

    return ReconciliationReport(_overall(issues), tuple(issues))

def reconcile_positions(
    local_positions: Iterable[BrokerPositionSnapshot],
    broker_positions: Iterable[BrokerPositionSnapshot],
) -> ReconciliationReport:
    local = {(p.broker_account_id, p.instrument_id): p for p in local_positions}
    broker = {(p.broker_account_id, p.instrument_id): p for p in broker_positions}
    issues: list[ReconciliationIssue] = []

    for key in local.keys() | broker.keys():
        lq = local.get(key).quantity if key in local else Decimal("0")
        bq = broker.get(key).quantity if key in broker else Decimal("0")
        if lq != bq:
            issues.append(ReconciliationIssue(
                "CRITICAL",
                "EXEC_POSITION_MISMATCH",
                {"account_id": key[0], "instrument_id": key[1], "local_qty": str(lq), "broker_qty": str(bq)}
            ))
    return ReconciliationReport(_overall(issues), tuple(issues))
