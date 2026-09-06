from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

@dataclass(frozen=True, slots=True)
class BufferedEvent:
    occurred_at: datetime
    event_type: str
    payload: Any
    approx_bytes: int

class RingBuffer:
    def __init__(self, *, max_events: int, max_bytes: int, max_age_seconds: int) -> None:
        if max_events <= 0 or max_bytes <= 0 or max_age_seconds <= 0:
            raise ValueError("ring buffer limits must be positive")
        self.max_events = max_events
        self.max_bytes = max_bytes
        self.max_age_seconds = max_age_seconds
        self._items = deque()
        self._bytes = 0

    def append(self, item: BufferedEvent) -> None:
        self._items.append(item)
        self._bytes += item.approx_bytes
        self._evict(item.occurred_at)

    def _evict(self, now: datetime) -> None:
        cutoff = now - timedelta(seconds=self.max_age_seconds)
        while self._items and (
            len(self._items) > self.max_events
            or self._bytes > self.max_bytes
            or self._items[0].occurred_at < cutoff
        ):
            old = self._items.popleft()
            self._bytes -= old.approx_bytes

    def snapshot(self) -> tuple[BufferedEvent, ...]:
        return tuple(self._items)

    @property
    def approx_bytes(self) -> int:
        return self._bytes

    def __len__(self) -> int:
        return len(self._items)
