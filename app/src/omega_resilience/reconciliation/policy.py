from __future__ import annotations
from omega_resilience.domain.models import ReconciliationResult

def reconciliation_reasons(r: ReconciliationResult) -> list[str]:
    reasons=list(r.reason_codes)
    if not r.positions_ok: reasons.append("RES_POSITION_MISMATCH")
    if not r.orders_ok: reasons.append("RES_ORDER_MISMATCH")
    if not r.accounts_ok or not r.database_ok: reasons.append("RES_RECONCILIATION_REQUIRED")
    if not r.balances_ok: reasons.append("RES_BALANCE_MISMATCH")
    return sorted(set(reasons))

def reconciliation_passed(r: ReconciliationResult) -> bool:
    return not reconciliation_reasons(r)
