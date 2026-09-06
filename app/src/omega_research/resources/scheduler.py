from __future__ import annotations

def should_pause_research(
    *,
    live_pressure: bool,
    thermal_pressure: bool,
    memory_pressure: bool,
    io_pressure: bool,
) -> tuple[bool, tuple[str,...]]:
    if any((live_pressure,thermal_pressure,memory_pressure,io_pressure)):
        return True,("RESEARCH_PAUSED_FOR_LIVE",)
    return False,()
