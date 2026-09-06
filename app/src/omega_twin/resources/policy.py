from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class ResourceBudget:
    max_parallel_replays: int | None = None
    max_parallel_monte_carlo_workers: int | None = None
    max_memory_mb: int | None = None
    max_cpu_pct: int | None = None

def should_pause_research(
    *,
    live_pressure: bool,
    thermal_pressure: bool,
    memory_pressure: bool,
    io_pressure: bool,
) -> bool:
    return any((live_pressure,thermal_pressure,memory_pressure,io_pressure))
