from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timedelta
from omega_resilience.domain.models import ServiceClass

LIMITS={
    ServiceClass.NONCRITICAL:5,
    ServiceClass.IMPORTANT:3,
    ServiceClass.CRITICAL:2,
}

class CrashLoopDetector:
    def __init__(self, window_seconds: int = 300):
        self.window_seconds=window_seconds
        self._restarts=defaultdict(list)

    def record_restart(self, service_id: str, at: datetime):
        xs=self._restarts[service_id]
        xs.append(at)
        cutoff=at-timedelta(seconds=self.window_seconds)
        self._restarts[service_id]=[x for x in xs if x>=cutoff]

    def is_crash_loop(self, service_id: str, service_class: ServiceClass, *, now: datetime) -> bool:
        cutoff=now-timedelta(seconds=self.window_seconds)
        xs=[x for x in self._restarts.get(service_id,[]) if x>=cutoff]
        return len(xs) >= LIMITS[service_class]

def restart_backoff_seconds(attempt: int, *, base: int = 2, maximum: int = 300) -> int:
    if attempt < 0:
        raise ValueError("attempt must be >= 0")
    return min(maximum, base*(2**attempt))
