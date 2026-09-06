from __future__ import annotations
from datetime import datetime
from omega_resilience.domain.models import Heartbeat, ServiceClass

TIMEOUTS = {
    ServiceClass.CRITICAL: 5,
    ServiceClass.IMPORTANT: 15,
    ServiceClass.NONCRITICAL: 60,
}

class HeartbeatRegistry:
    def __init__(self) -> None:
        self._latest={}
        self._counter_history={}

    def ingest(self, hb: Heartbeat) -> None:
        current=self._latest.get(hb.service_id)
        if current and hb.sent_at < current.sent_at:
            return
        self._latest[hb.service_id]=hb
        h=self._counter_history.setdefault(hb.service_id,[])
        h.append(hb.counter)
        if len(h)>10:
            del h[:-10]

    def latest(self, service_id: str):
        return self._latest.get(service_id)

    def stale(self, service_id: str, service_class: ServiceClass, *, now: datetime, timeout_override: int | None=None) -> bool:
        hb=self._latest.get(service_id)
        if hb is None:
            return True
        timeout=timeout_override if timeout_override is not None else TIMEOUTS[service_class]
        return (now-hb.sent_at).total_seconds() > timeout

    def stuck_counter(self, service_id: str, checks: int = 3) -> bool:
        xs=self._counter_history.get(service_id,[])
        if len(xs)<checks:
            return False
        tail=xs[-checks:]
        return len(set(tail))==1
