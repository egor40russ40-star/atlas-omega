from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Mapping, Any, Optional
from uuid import UUID

class RiskDecisionStatus(str, Enum):
    APPROVED = "APPROVED"
    REDUCED = "REDUCED"
    DENIED = "DENIED"

class CrisisMode(str, Enum):
    NORMAL = "NORMAL"
    CAUTION = "CAUTION"
    DEFENSIVE = "DEFENSIVE"
    SAFE = "SAFE"
    EMERGENCY = "EMERGENCY"

@dataclass(frozen=True, slots=True)
class RiskRequest:
    request_id: UUID
    intent_id: UUID
    strategy_id: str
    account_id: str
    account_role: str
    instrument_id: str
    side: str
    requested_risk_rub: Decimal
    requested_capital_rub: Decimal
    requested_borrowed_increment_rub: Decimal
    market_snapshot_id: str

@dataclass(frozen=True, slots=True)
class RiskContext:
    realized_pnl_rub: Decimal
    unrealized_pnl_rub: Decimal
    portfolio_equity_rub: Decimal
    portfolio_high_water_rub: Decimal
    strategy_open_risk_rub: Decimal
    account_open_risk_rub: Decimal
    portfolio_open_risk_rub: Decimal
    instrument_exposure_rub: Decimal
    current_borrowed_long_rub: Decimal
    current_borrowed_hedge_rub: Decimal
    consecutive_losses: int
    market_data_age_seconds: Decimal
    broker_state_age_seconds: Decimal
    data_quality_score: Decimal
    reconciliation_status: str
    crisis_mode: CrisisMode
    kill_switch: bool
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class RiskLimits:
    daily_loss_limit_rub: Optional[Decimal] = None
    hard_drawdown_limit_rub: Optional[Decimal] = None
    strategy_open_risk_limit_rub: Optional[Decimal] = None
    account_open_risk_limit_rub: Optional[Decimal] = None
    portfolio_open_risk_limit_rub: Optional[Decimal] = None
    max_instrument_concentration_pct: Optional[Decimal] = None
    max_consecutive_losses_before_caution: int = 3
    max_consecutive_losses_before_safe: int = 5
    rosn_borrowed_long_limit_rub: Decimal = Decimal("5000")
    rosn_borrowed_hedge_limit_rub: Decimal = Decimal("5000")
    min_data_quality_score: Decimal = Decimal("0.80")
    max_market_data_age_seconds: Decimal = Decimal("5")
    max_broker_state_age_seconds: Decimal = Decimal("10")

@dataclass(frozen=True, slots=True)
class RiskDecision:
    request_id: UUID
    status: RiskDecisionStatus
    approved_risk_rub: Decimal
    approved_capital_rub: Decimal
    reason_codes: tuple[str, ...]
    policy_hash: str
    valid_until: datetime
