from __future__ import annotations
from dataclasses import dataclass
from omega_resilience.domain.models import RecoveryState

@dataclass(frozen=True, slots=True)
class UpdateDecision:
    allowed: bool
    reason_codes: tuple[str,...]

def update_allowed(state: RecoveryState, *, snapshot_created: bool, package_verified: bool) -> UpdateDecision:
    reasons=[]
    if state not in {RecoveryState.SAFE,RecoveryState.RECOVERY}:
        reasons.append("RES_UPDATE_REQUIRES_SAFE")
    if not snapshot_created or not package_verified:
        reasons.append("RES_UPDATE_REQUIRES_SAFE")
    return UpdateDecision(not reasons,tuple(sorted(set(reasons))))

def rollback_required(*, post_update_self_test_ok: bool, reconciliation_ok: bool) -> bool:
    return not (post_update_self_test_ok and reconciliation_ok)
