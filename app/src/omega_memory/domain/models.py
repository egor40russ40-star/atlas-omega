from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Mapping, Any, Optional
from uuid import UUID

class ObservationMode(str, Enum):
    REAL = "REAL"
    SHADOW = "SHADOW"
    SANDBOX = "SANDBOX"
    REPLAY = "REPLAY"
    COUNTERFACTUAL = "COUNTERFACTUAL"

class WaitOutcomeClass(str, Enum):
    AVOIDED_BAD = "AVOIDED_BAD"
    MISSED_GOOD = "MISSED_GOOD"
    NEUTRAL = "NEUTRAL"
    INCOMPLETE = "INCOMPLETE"
    UNEVALUABLE = "UNEVALUABLE"

class CounterfactualType(str, Enum):
    ENTRY_OFFSET = "ENTRY_OFFSET"
    ENTRY_DELAY = "ENTRY_DELAY"
    STOP_MULTIPLIER = "STOP_MULTIPLIER"
    TP_MULTIPLIER = "TP_MULTIPLIER"
    PARTIAL_TAKE = "PARTIAL_TAKE"
    NO_PARTIAL = "NO_PARTIAL"
    TRAILING = "TRAILING"
    NO_TRADE = "NO_TRADE"

@dataclass(frozen=True, slots=True)
class MarketObservation:
    observation_id: UUID
    instrument_id: str
    observed_at: datetime
    world_model_id: str
    feature_vector: Mapping[str, float]
    source_mode: ObservationMode
    strategic_bias: str
    router_action: str
    selected_strategy_id: Optional[str]
    wait_reason_codes: tuple[str, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class PricePoint:
    occurred_at: datetime
    price: Decimal
    high: Decimal
    low: Decimal

@dataclass(frozen=True, slots=True)
class HorizonOutcome:
    horizon_seconds: int
    start_price: Decimal
    end_price: Optional[Decimal]
    return_pct: Optional[Decimal]
    high: Optional[Decimal]
    low: Optional[Decimal]
    mfe_long_pct: Optional[Decimal]
    mae_long_pct: Optional[Decimal]
    mfe_short_pct: Optional[Decimal]
    mae_short_pct: Optional[Decimal]
    path_complete: bool

@dataclass(frozen=True, slots=True)
class ObservationOutcome:
    outcome_id: UUID
    observation_id: UUID
    labeled_at: datetime
    horizons: Mapping[int, HorizonOutcome]
    source_mode: ObservationMode
    lineage: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class WaitEvaluation:
    evaluation_id: UUID
    observation_id: UUID
    strategy_id: Optional[str]
    reason_codes: tuple[str, ...]
    direction: Optional[str]
    outcome_class: WaitOutcomeClass
    evaluated_horizon_seconds: Optional[int]
    utility_r: Optional[Decimal]
    details: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class SimilarObservation:
    observation_id: UUID
    distance: float
    similarity: float
    observed_at: datetime
    source_mode: ObservationMode

@dataclass(frozen=True, slots=True)
class CounterfactualScenario:
    scenario_id: UUID
    parent_observation_id: UUID
    scenario_type: CounterfactualType
    scenario_version: str
    side: str
    entry_price: Decimal
    stop_price: Optional[Decimal]
    take_profit_price: Optional[Decimal]
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class CounterfactualResult:
    result_id: UUID
    scenario_id: UUID
    parent_observation_id: UUID
    source_mode: ObservationMode
    entry_price: Optional[Decimal]
    exit_price: Optional[Decimal]
    exit_reason: str
    pnl_points: Optional[Decimal]
    pnl_r: Optional[Decimal]
    mfe_points: Optional[Decimal]
    mae_points: Optional[Decimal]
    duration_seconds: Optional[int]
    path_complete: bool
    lineage: Mapping[str, Any] = field(default_factory=dict)
