from __future__ import annotations
from decimal import Decimal
from omega_resilience.domain.models import NetworkSnapshot

def network_reasons(
    x: NetworkSnapshot,
    *,
    latency_warning_ms=Decimal("500"),
    latency_critical_ms=Decimal("1500"),
    loss_warning_pct=Decimal("2"),
    loss_critical_pct=Decimal("10"),
) -> tuple[str,...]:
    if not x.reachable:
        return ("RES_NETWORK_CRITICAL",)
    if x.latency_ms is not None and x.latency_ms >= latency_critical_ms:
        return ("RES_NETWORK_CRITICAL",)
    if x.packet_loss_pct >= loss_critical_pct:
        return ("RES_NETWORK_CRITICAL",)
    if (
        (x.latency_ms is not None and x.latency_ms >= latency_warning_ms)
        or x.packet_loss_pct >= loss_warning_pct
    ):
        return ("RES_NETWORK_DEGRADED",)
    return ()
