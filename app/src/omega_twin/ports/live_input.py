from __future__ import annotations
from typing import Protocol, Iterable
from omega_twin.domain.models import ReplayEvent

class TwinInputPort(Protocol):
    def stream(self) -> Iterable[ReplayEvent]: ...

class TwinResultPort(Protocol):
    def append_event(self, event_type: str, payload: dict) -> None: ...
