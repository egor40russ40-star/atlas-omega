from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

@dataclass(slots=True)
class ReplayClock:
    current_time: datetime

    def advance_to(self, t: datetime) -> None:
        if t < self.current_time:
            raise ValueError("replay clock cannot move backwards")
        self.current_time=t

    def assert_available(self, data_time: datetime) -> None:
        if data_time > self.current_time:
            raise ValueError("MEMORY_FUTURE_NEIGHBOUR_BLOCKED")
