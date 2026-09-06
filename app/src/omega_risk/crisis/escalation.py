from __future__ import annotations
from omega_risk.domain.models import CrisisMode

def suggested_mode_for_loss_streak(
    current_mode: CrisisMode,
    consecutive_losses: int,
    caution_at: int,
    safe_at: int,
) -> CrisisMode:
    if consecutive_losses >= safe_at:
        return CrisisMode.SAFE
    if consecutive_losses >= caution_at:
        if current_mode is CrisisMode.NORMAL:
            return CrisisMode.CAUTION
    return current_mode
