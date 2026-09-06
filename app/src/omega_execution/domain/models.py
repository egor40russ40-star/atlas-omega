from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Mapping, Any, Optional
from uuid import UUID

class OrderState(str, Enum):
    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    SUBMITTING = "SUBMITTING"
    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCEL_REQUESTED = "CANCEL_REQUESTED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    UNKNOWN_OUTCOME = "UNKNOWN_OUTCOME"
    RECONCILING = "RECONCILING"
    SAFE_RETRY_ALLOWED = "SAFE_RETRY_ALLOWED"
    RECOVERY_REQUIRED = "RECOVERY_REQUIRED"

class BrokerSubmitStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    TIMEOUT = "TIMEOUT"
    CONNECTION_LOST = "CONNECTION_LOST"
    UNKNOWN = "UNKNOWN"

@dataclass(frozen=True, slots=True)
class InstrumentRules:
    instrument_id: str
    lot_size: Decimal
    quantity_step: Decimal
    price_step: Decimal
    min_quantity: Decimal = Decimal("1")

@dataclass(frozen=True, slots=True)
class ExecutionRequest:
    execution_request_id: UUID
    intent_id: UUID
    broker_account_id: str
    instrument_id: str
    side: str
    quantity: Decimal
    order_style: str
    created_at: datetime
    valid_until: datetime
    approval_chain_hash: str
    idempotency_key: str
    limit_price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    market_snapshot_id: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class BrokerSubmitResult:
    status: BrokerSubmitStatus
    broker_order_id: Optional[str] = None
    message: Optional[str] = None
    raw: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class BrokerOrderSnapshot:
    broker_order_id: str
    broker_account_id: str
    instrument_id: str
    side: str
    state: str
    requested_quantity: Decimal
    filled_quantity: Decimal
    average_fill_price: Optional[Decimal]
    client_tag: Optional[str] = None

@dataclass(frozen=True, slots=True)
class BrokerPositionSnapshot:
    broker_account_id: str
    instrument_id: str
    quantity: Decimal
    average_price: Optional[Decimal] = None
