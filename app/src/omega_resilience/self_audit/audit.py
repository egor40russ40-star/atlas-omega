from __future__ import annotations
from datetime import datetime
from omega_resilience.domain.models import SelfAuditCheck, SelfAuditReport

def build_report(*, created_at: datetime, checks: list[SelfAuditCheck]) -> SelfAuditReport:
    blocking_failed=[c for c in checks if not c.passed and c.blocking]
    passed=not blocking_failed
    reasons=[]
    for c in checks:
        if not c.passed:
            reasons.extend(c.reason_codes)
    reasons.append("RES_SELF_AUDIT_PASS" if passed else "RES_SELF_AUDIT_FAIL")
    return SelfAuditReport(
        created_at,tuple(checks),passed,passed,tuple(sorted(set(reasons)))
    )
