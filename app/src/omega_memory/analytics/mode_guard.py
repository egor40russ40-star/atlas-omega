from __future__ import annotations
from omega_memory.domain.models import ObservationMode

def validate_mode_mix(modes, *, allow_explicit_mix: bool = False) -> None:
    modes=set(modes)
    if len(modes) <= 1:
        return
    if allow_explicit_mix:
        return
    # REAL may not silently mix with research modes.
    if ObservationMode.REAL in modes or ObservationMode.COUNTERFACTUAL in modes:
        raise ValueError("MEMORY_MODE_MIX_FORBIDDEN")
