from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional, Mapping, Sequence
from uuid import UUID
from omega_data.domain.models import EventEnvelope  # canonical Event Envelope v2

class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStyle(str, Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"

class DecisionStatus(str, Enum):
    APPROVED = "APPROVED"
    REDUCED = "REDUCED"
    DENIED = "DENIED"

@dataclass(frozen=True, slots=True)
class TradeIntent:
    intent_id: UUID
    created_at: datetime
    strategy_id: str
    account_role: str
    instrument_id: str
    side: Side
    quantity: Decimal
    order_style: OrderStyle
    reason_codes: Sequence[str]
    market_snapshot_id: str
    limit_price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    requested_capital: Optional[Decimal] = None
    requested_risk: Optional[Decimal] = None
    confidence: Optional[Decimal] = None
    setup_type: Optional[str] = None
    valid_until: Optional[datetime] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class Decision:
    decision_id: UUID
    status: DecisionStatus
    decided_at: datetime
    reason_codes: Sequence[str]
    valid_until: Optional[datetime] = None
    approved_capital: Optional[Decimal] = None
    approved_risk: Optional[Decimal] = None
    decision_hash: Optional[str] = None
