from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class ReadinessInput:
    self_test_ok: bool
    broker_connected: bool
    accounts_synced: bool
    positions_synced: bool
    orders_synced: bool
    database_reconciled: bool
    risk_rebuilt: bool
    market_data_healthy: bool
    kill_switch_active: bool
    critical_services_healthy: bool
    clock_ok: bool
    storage_ok: bool

def readiness_reasons(x: ReadinessInput) -> list[str]:
    r=[]
    if not x.self_test_ok: r.append("RES_SELF_AUDIT_FAIL")
    if not x.broker_connected: r.append("RES_DEPENDENCY_DOWN")
    if not x.accounts_synced: r.append("RES_RECONCILIATION_REQUIRED")
    if not x.positions_synced: r.append("RES_POSITION_MISMATCH")
    if not x.orders_synced: r.append("RES_ORDER_MISMATCH")
    if not x.database_reconciled: r.append("RES_RECONCILIATION_REQUIRED")
    if not x.risk_rebuilt: r.append("RES_RECONCILIATION_REQUIRED")
    if not x.market_data_healthy: r.append("RES_DEPENDENCY_DOWN")
    if x.kill_switch_active: r.append("RES_SELF_AUDIT_FAIL")
    if not x.critical_services_healthy: r.append("RES_HEARTBEAT_STALE")
    if not x.clock_ok: r.append("RES_CLOCK_DRIFT")
    if not x.storage_ok: r.append("RES_DISK_PRESSURE")
    return sorted(set(r))

def ready_allowed(x: ReadinessInput) -> bool:
    return not readiness_reasons(x)
