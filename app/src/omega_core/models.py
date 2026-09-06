from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from decimal import Decimal
from typing import Mapping, Any, Optional, Sequence
from uuid import UUID

class ReconciliationSeverity(str, Enum):
    OK = "OK"
    WARNING = "WARNING"
    BLOCKING = "BLOCKING"
    CRITICAL = "CRITICAL"

class OrderState(str, Enum):
    CREATED = "CREATED"
    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCEL_REQUESTED = "CANCEL_REQUESTED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    UNKNOWN = "UNKNOWN"

@dataclass(frozen=True, slots=True)
class ExecutionRequest:
    execution_request_id: UUID
    intent_id: UUID
    idempotency_key: str
    approval_chain_hash: str
    broker_account_id: str
    instrument_id: str
    side: str
    quantity: Decimal
    order_style: str
    created_at: datetime
    valid_until: datetime
    limit_price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    market_snapshot_id: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class ReconciliationCheck:
    check_type: str
    status: ReconciliationSeverity
    reason_codes: Sequence[str]
    details: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class ReconciliationResult:
    reconciliation_id: UUID
    started_at: datetime
    finished_at: datetime
    status: ReconciliationSeverity
    checks: Sequence[ReconciliationCheck]
