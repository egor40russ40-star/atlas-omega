from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Mapping, Any, Optional
from uuid import UUID

@dataclass(frozen=True, slots=True)
class LedgerPosting:
    posting_id: UUID
    ledger_account: str
    currency: str
    amount: Decimal
    broker_account_id: Optional[str] = None
    strategy_id: Optional[str] = None
    instrument_id: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class LedgerTransaction:
    transaction_id: UUID
    occurred_at: datetime
    event_type: str
    source_type: str
    source_id: Optional[str]
    broker_operation_id: Optional[str]
    description_ru: str
    postings: tuple[LedgerPosting, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)
