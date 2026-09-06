from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from decimal import Decimal

@dataclass(frozen=True, slots=True)
class ShadowDecisionRecord:
    record_id: UUID
    strategy_id: str
    proposal_id: UUID
    world_model_id: str
    created_at: datetime
    action: str
    side: str | None
    entry_price: Decimal | None
    score: Decimal
    outcome_label: str | None = None
    outcome_at: datetime | None = None
