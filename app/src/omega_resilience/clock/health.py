from __future__ import annotations
from decimal import Decimal
from omega_resilience.domain.models import ClockSnapshot

def clock_ok(x: ClockSnapshot, *, max_offset_ms: Decimal) -> bool:
    return x.synchronized and abs(x.offset_ms) <= max_offset_ms

def clock_reasons(x: ClockSnapshot, *, max_offset_ms: Decimal) -> tuple[str,...]:
    return () if clock_ok(x,max_offset_ms=max_offset_ms) else ("RES_CLOCK_DRIFT",)
