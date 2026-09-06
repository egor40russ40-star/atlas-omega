from __future__ import annotations
from decimal import Decimal
from omega_resilience.domain.models import ResourceSnapshot

def resource_reasons(
    x: ResourceSnapshot,
    *,
    cpu_caution=Decimal("85"),
    cpu_critical=Decimal("95"),
    memory_caution=Decimal("85"),
    memory_critical=Decimal("95"),
    disk_caution_free=Decimal("15"),
    disk_critical_free=Decimal("7"),
    temp_caution=Decimal("85"),
    temp_critical=Decimal("95"),
) -> tuple[str,...]:
    r=[]
    if x.cpu_pct >= cpu_caution: r.append("RES_CPU_PRESSURE")
    if x.memory_pct >= memory_caution: r.append("RES_MEMORY_PRESSURE")
    if x.disk_free_pct <= disk_caution_free: r.append("RES_DISK_PRESSURE")
    if x.temperature_c is not None and x.temperature_c >= temp_caution: r.append("RES_THERMAL_PRESSURE")
    return tuple(sorted(set(r)))

def resource_mode(x: ResourceSnapshot) -> str:
    critical = (
        x.cpu_pct >= Decimal("95")
        or x.memory_pct >= Decimal("95")
        or x.disk_free_pct <= Decimal("7")
        or (x.temperature_c is not None and x.temperature_c >= Decimal("95"))
    )
    if critical: return "CRITICAL"
    if resource_reasons(x): return "CAUTION"
    return "NORMAL"

def background_actions(mode: str) -> tuple[str,...]:
    if mode=="NORMAL": return ()
    if mode=="CAUTION":
        return ("THROTTLE_AI","THROTTLE_REPLAY","REDUCE_MONTE_CARLO")
    return ("STOP_AI","STOP_RESEARCH","STOP_REPLAY","PROTECT_LIVE_RESOURCES")
