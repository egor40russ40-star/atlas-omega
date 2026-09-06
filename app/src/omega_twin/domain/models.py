from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Mapping, Any, Optional
from uuid import UUID

class ReplayMode(str, Enum):
    TWIN = "TWIN"
    REPLAY = "REPLAY"
    BACKTEST = "BACKTEST"
    WALK_FORWARD = "WALK_FORWARD"
    ADVERSARIAL = "ADVERSARIAL"

class SimOrderState(str, Enum):
    CREATED = "CREATED"
    ACCEPTED = "ACCEPTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCEL_REQUESTED = "CANCEL_REQUESTED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    UNKNOWN_OUTCOME = "UNKNOWN_OUTCOME"

class PromotionDecision(str, Enum):
    PASS = "PASS"
    CONDITIONAL = "CONDITIONAL"
    FAIL = "FAIL"

@dataclass(frozen=True, slots=True)
class ReplayEvent:
    event_id: UUID
    occurred_at: datetime
    sequence: int
    event_type: str
    payload: Mapping[str, Any]

@dataclass(frozen=True, slots=True)
class MarketBar:
    opened_at: datetime
    closed_at: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    spread: Decimal = Decimal("0")

@dataclass(frozen=True, slots=True)
class SimOrder:
    order_id: UUID
    client_id: str
    instrument_id: str
    side: str
    order_type: str
    quantity: Decimal
    remaining_quantity: Decimal
    state: SimOrderState
    created_at: datetime
    limit_price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    filled_quantity: Decimal = Decimal("0")
    average_fill_price: Optional[Decimal] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class SimFill:
    fill_id: UUID
    order_id: UUID
    occurred_at: datetime
    quantity: Decimal
    price: Decimal
    commission: Decimal
    slippage: Decimal

@dataclass(frozen=True, slots=True)
class TradeResult:
    trade_id: UUID
    strategy_id: str
    opened_at: datetime
    closed_at: datetime
    side: str
    pnl_r: Decimal
    pnl_r_after_costs: Decimal
    pnl_money: Decimal
    commission: Decimal
    slippage_cost: Decimal
    max_favorable_r: Decimal
    max_adverse_r: Decimal
    safety_violations: int = 0
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class ValidationMetrics:
    trades: int
    win_rate: Decimal
    expectancy_r: Decimal
    expectancy_r_after_costs: Decimal
    profit_factor: Decimal | None
    max_drawdown_r: Decimal
    max_consecutive_losses: int
    total_commission: Decimal
    total_slippage_cost: Decimal
    safety_violations: int

@dataclass(frozen=True, slots=True)
class ExperimentManifest:
    experiment_id: UUID
    name: str
    mode: ReplayMode
    dataset_id: str
    dataset_hash: str
    code_version: str
    config_hash: str
    strategy_versions: Mapping[str, str]
    router_version: str
    risk_version: str
    broker_sim_version: str
    cost_model_version: str
    slippage_model_version: str
    latency_model_version: str
    random_seed: int
    start_at: datetime
    end_at: datetime
    created_at: datetime
    hardware_profile_id: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class PromotionReport:
    challenger_id: str
    champion_id: Optional[str]
    decision: PromotionDecision
    reason_codes: tuple[str, ...]
    metrics: ValidationMetrics
    walkforward_folds: int
    monte_carlo_p95_drawdown_r: Optional[Decimal]
    adversarial_pass_rate: Decimal
    shadow_samples: int
    sandbox_samples: int
    reproducible: bool
    metadata: Mapping[str, Any] = field(default_factory=dict)
