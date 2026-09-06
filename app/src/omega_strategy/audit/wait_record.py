from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass(frozen=True, slots=True)
class WaitRecord:
    wait_id: UUID
    strategy_id: str
    world_model_id: str
    created_at: datetime
    reason_codes: tuple[str, ...]
    missing_conditions: tuple[str, ...]
    recheck_after_seconds: int
    outcome_attached: bool = False
