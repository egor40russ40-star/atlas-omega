from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class StoragePressure(str, Enum):
    NORMAL = "NORMAL"
    CAUTION = "CAUTION"
    DEFENSIVE = "DEFENSIVE"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"

@dataclass(frozen=True, slots=True)
class PressureThresholds:
    caution_free_pct: float
    defensive_free_pct: float
    critical_free_pct: float
    emergency_free_pct: float

def classify_pressure(free_pct: float, t: PressureThresholds) -> StoragePressure:
    if free_pct <= t.emergency_free_pct:
        return StoragePressure.EMERGENCY
    if free_pct <= t.critical_free_pct:
        return StoragePressure.CRITICAL
    if free_pct <= t.defensive_free_pct:
        return StoragePressure.DEFENSIVE
    if free_pct <= t.caution_free_pct:
        return StoragePressure.CAUTION
    return StoragePressure.NORMAL

def actions_for_pressure(p: StoragePressure) -> tuple[str, ...]:
    if p is StoragePressure.NORMAL:
        return ()
    if p is StoragePressure.CAUTION:
        return ("THROTTLE_AI", "ROTATE_TEMP")
    if p is StoragePressure.DEFENSIVE:
        return ("STOP_BACKTEST", "STOP_NEW_REPLAY", "THROTTLE_RESEARCH", "AGGRESSIVE_WARM_COMPACTION")
    if p is StoragePressure.CRITICAL:
        return (
            "STOP_AI", "STOP_RESEARCH", "STOP_REPLAY",
            "STOP_OPTIONAL_RAW_ARCHIVE", "PROTECT_LIVE_RESERVE",
            "BLOCK_NEW_ENTRIES_IF_DURABILITY_AT_RISK",
        )
    return (
        "STOP_AI", "STOP_RESEARCH", "STOP_REPLAY",
        "STOP_OPTIONAL_RAW_ARCHIVE", "PROTECT_LIVE_RESERVE",
        "ENTER_SAFE", "CAPTURE_BLACKBOX",
    )
