from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

@dataclass(slots=True)
class ReplayClock:
    current_time: datetime

    def advance_to(self, t: datetime) -> None:
        if t < self.current_time:
            raise ValueError("TWIN_CLOCK_BACKWARD_BLOCKED")
        self.current_time = t

    def assert_available(self, event_time: datetime) -> None:
        if event_time > self.current_time:
            raise ValueError("TWIN_FUTURE_EVENT_BLOCKED")
