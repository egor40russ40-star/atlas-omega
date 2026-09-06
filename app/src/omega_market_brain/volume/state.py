from __future__ import annotations
from decimal import Decimal
from omega_market_brain.domain.models import VolumeState

def volume_ratio(current: Decimal, baseline: Decimal | None) -> Decimal | None:
    if baseline is None or baseline <= 0:
        return None
    return current / baseline

def classify_volume(ratio: Decimal | None) -> VolumeState:
    if ratio is None:
        return VolumeState.UNKNOWN
    if ratio < Decimal("0.4"):
        return VolumeState.VERY_LOW
    if ratio < Decimal("0.8"):
        return VolumeState.LOW
    if ratio < Decimal("1.3"):
        return VolumeState.NORMAL
    if ratio < Decimal("2.0"):
        return VolumeState.HIGH
    return VolumeState.EXTREME
