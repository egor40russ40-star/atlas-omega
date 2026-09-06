from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Mapping, Any, Optional
from uuid import UUID

class StrategyRole(str, Enum):
    LAB = "LAB"
    SHADOW = "SHADOW"
    SANDBOX = "SANDBOX"
    CHALLENGER = "CHALLENGER"
    CHAMPION = "CHAMPION"
    LIVE_DISABLED = "LIVE_DISABLED"

class StrategyAction(str, Enum):
    WAIT = "WAIT"
    LONG_PROPOSAL = "LONG_PROPOSAL"
    SHORT_PROPOSAL = "SHORT_PROPOSAL"
    HEDGE_PROPOSAL = "HEDGE_PROPOSAL"
    EXIT_PROPOSAL = "EXIT_PROPOSAL"
    MANAGE_PROPOSAL = "MANAGE_PROPOSAL"
    PROTECTIVE_PROPOSAL = "PROTECTIVE_PROPOSAL"

class ProposalClass(str, Enum):
    PROTECTIVE = "PROTECTIVE"
    EXIT = "EXIT"
    HEDGE = "HEDGE"
    ENTRY = "ENTRY"
    WAIT = "WAIT"

@dataclass(frozen=True, slots=True)
class StrategyDescriptor:
    strategy_id: str
    name_ru: str
    instrument_id: str
    role: StrategyRole
    family: str
    version: str
    live_permission: bool = False
    sandbox_only: bool = False
    independent_family: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class StrategyContext:
    now: datetime
    account_role: str
    position_quantity: Decimal
    position_average_price: Optional[Decimal]
    own_funds_rub: Decimal
    borrowed_funds_rub: Decimal
    active_orders: tuple[Mapping[str, Any], ...] = ()
    daily_ideas_used_strategy: int = 0
    daily_ideas_used_instrument: int = 0
    daily_ideas_used_total: int = 0
    last_stop_at: Optional[datetime] = None
    last_entry_at: Optional[datetime] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class ScoreComponents:
    setup_quality: Decimal
    regime_fit: Decimal
    timeframe_alignment: Decimal
    orderflow_support: Decimal
    level_quality: Decimal
    context_support: Decimal
    historical_quality: Decimal
    execution_readiness: Decimal
    data_quality: Decimal
    uncertainty_penalty: Decimal

@dataclass(frozen=True, slots=True)
class StrategyProposal:
    proposal_id: UUID
    strategy_id: str
    instrument_id: str
    created_at: datetime
    action: StrategyAction
    proposal_class: ProposalClass
    side: Optional[str]
    entry_price: Optional[Decimal]
    stop_price: Optional[Decimal]
    take_profit_price: Optional[Decimal]
    requested_quantity: Optional[Decimal]
    requested_capital_rub: Optional[Decimal]
    requested_risk_rub: Optional[Decimal]
    confidence: Decimal
    score_components: ScoreComponents
    reason_codes: tuple[str, ...]
    world_model_id: str
    expires_at: datetime
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class StrategyScore:
    proposal_id: UUID
    final_score: Decimal
    reason_codes: tuple[str, ...]

@dataclass(frozen=True, slots=True)
class RouterDecision:
    selected_proposal_id: Optional[UUID]
    selected_strategy_id: Optional[str]
    action: str
    final_score: Decimal
    reason_codes: tuple[str, ...]
    considered_proposals: tuple[UUID, ...]
    live_candidate: bool
    metadata: Mapping[str, Any] = field(default_factory=dict)
