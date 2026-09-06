from __future__ import annotations
from typing import Iterable, Callable
from omega_twin.domain.models import ReplayEvent
from omega_twin.clock.replay_clock import ReplayClock

def deterministic_order(events: Iterable[ReplayEvent]) -> list[ReplayEvent]:
    return sorted(events, key=lambda e: (e.occurred_at, e.sequence, str(e.event_id)))

def replay(
    events: Iterable[ReplayEvent],
    *,
    clock: ReplayClock,
    handler: Callable[[ReplayEvent, ReplayClock], None],
) -> int:
    count = 0
    for event in deterministic_order(events):
        clock.advance_to(event.occurred_at)
        handler(event, clock)
        count += 1
    return count
