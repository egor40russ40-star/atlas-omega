from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Mapping, Any, Optional
from uuid import UUID

Money = Decimal

class AccountRole(str, Enum):
    ROSN_PRIMARY = "ROSN_PRIMARY"
    ROSN_HEDGE = "ROSN_HEDGE"
    CNYRUBF_DEDICATED = "CNYRUBF_DEDICATED"
    RESEARCH_ONLY = "RESEARCH_ONLY"
    RESERVE = "RESERVE"
    UNASSIGNED = "UNASSIGNED"

class AccountState(str, Enum):
    DISCOVERED = "DISCOVERED"
    UNASSIGNED = "UNASSIGNED"
    ASSIGNED = "ASSIGNED"
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    LOCKED = "LOCKED"
    CLOSED = "CLOSED"

class LedgerEventType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRADE_PROFIT = "TRADE_PROFIT"
    TRADE_LOSS = "TRADE_LOSS"
    COMMISSION = "COMMISSION"
    DIVIDEND = "DIVIDEND"
    COUPON = "COUPON"
    TAX = "TAX"
    POSITION_OPEN = "POSITION_OPEN"
    POSITION_CLOSE = "POSITION_CLOSE"
    ORDER_RESERVE = "ORDER_RESERVE"
    ORDER_RELEASE = "ORDER_RELEASE"
    MARGIN_USED = "MARGIN_USED"
    MARGIN_RELEASED = "MARGIN_RELEASED"
    INTERNAL_TRANSFER = "INTERNAL_TRANSFER"
    INTERNAL_ALLOCATION = "INTERNAL_ALLOCATION"
    BROKER_CORRECTION = "BROKER_CORRECTION"
    UNCLASSIFIED_BALANCE_CHANGE = "UNCLASSIFIED_BALANCE_CHANGE"

class CapitalDecisionStatus(str, Enum):
    APPROVED = "APPROVED"
    REDUCED = "REDUCED"
    DENIED = "DENIED"

@dataclass(frozen=True, slots=True)
class AccountRecord:
    internal_account_id: UUID
    broker_account_id: str
    display_name_ru: str
    role: AccountRole
    state: AccountState
    allowed_strategies: tuple[str, ...] = ()
    allowed_instruments: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class BrokerMoneySnapshot:
    account_id: UUID
    captured_at: datetime
    currency: str
    cash: Money
    total_equity: Money
    available_cash: Money
    margin_used: Money
    borrowed_funds: Money
    payload_hash: str

@dataclass(frozen=True, slots=True)
class CapitalRequest:
    request_id: UUID
    strategy_id: str
    account_id: UUID
    instrument_id: str
    requested_capital: Money
    requested_risk: Money
    requested_borrowed_increment: Money = Decimal("0")
    purpose: str = "ENTRY"

@dataclass(frozen=True, slots=True)
class CapitalDecision:
    request_id: UUID
    status: CapitalDecisionStatus
    approved_capital: Money
    approved_risk: Money
    approved_borrowed_increment: Money
    reason_codes: tuple[str, ...]
