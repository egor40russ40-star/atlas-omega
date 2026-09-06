from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Mapping, Any, Optional

class Direction(str, Enum):
    STRONG_DOWN = "STRONG_DOWN"
    DOWN = "DOWN"
    NEUTRAL = "NEUTRAL"
    UP = "UP"
    STRONG_UP = "STRONG_UP"

class StructureState(str, Enum):
    TREND = "TREND"
    PULLBACK = "PULLBACK"
    RANGE = "RANGE"
    COMPRESSION = "COMPRESSION"
    BREAKOUT = "BREAKOUT"
    RETEST = "RETEST"
    TRANSITION = "TRANSITION"
    UNKNOWN = "UNKNOWN"

class VolumeState(str, Enum):
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    EXTREME = "EXTREME"
    UNKNOWN = "UNKNOWN"

class LiquidityState(str, Enum):
    GOOD = "GOOD"
    NORMAL = "NORMAL"
    THIN = "THIN"
    POOR = "POOR"
    UNKNOWN = "UNKNOWN"

class UncertaintyLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"

@dataclass(frozen=True, slots=True)
class Candle:
    opened_at: datetime
    closed_at: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

@dataclass(frozen=True, slots=True)
class Level:
    price: Decimal
    kind: str
    strength: Decimal
    touches: int
    last_touched_at: datetime | None = None

@dataclass(frozen=True, slots=True)
class TimeframeState:
    timeframe: str
    direction_score: Decimal
    direction: Direction
    structure: StructureState
    confidence: Decimal
    support: Optional[Level]
    resistance: Optional[Level]
    atr: Optional[Decimal]
    atr_pct: Optional[Decimal]
    realized_vol: Optional[Decimal]
    volume_ratio: Optional[Decimal]
    volume_state: VolumeState
    data_quality_score: Decimal
    flags: tuple[str, ...] = ()

@dataclass(frozen=True, slots=True)
class OrderFlowState:
    spread_pct: Decimal
    bid_ask_imbalance: Decimal
    pressure_score: Decimal
    liquidity_state: LiquidityState
    absorption_bid: bool = False
    absorption_ask: bool = False
    sweep_up: bool = False
    sweep_down: bool = False
    confidence: Decimal = Decimal("0")

@dataclass(frozen=True, slots=True)
class ContextNode:
    name: str
    value: Decimal
    direction: Decimal
    confidence: Decimal
    freshness: Decimal
    source_quality: Decimal
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class ContextGraphState:
    instrument_id: str
    nodes: tuple[ContextNode, ...]
    aggregate_score: Decimal
    conflict_score: Decimal
    freshness_score: Decimal
    reason_codes: tuple[str, ...] = ()

@dataclass(frozen=True, slots=True)
class RegimeProbabilities:
    trend_up: Decimal
    trend_down: Decimal
    range: Decimal
    compression: Decimal
    breakout_up: Decimal
    breakout_down: Decimal
    transition: Decimal
    high_volatility: Decimal
    low_liquidity: Decimal

@dataclass(frozen=True, slots=True)
class UncertaintyState:
    score: Decimal
    level: UncertaintyLevel
    reason_codes: tuple[str, ...]

@dataclass(frozen=True, slots=True)
class WorldModelSnapshot:
    instrument_id: str
    captured_at: datetime
    price: Decimal
    timeframes: Mapping[str, TimeframeState]
    orderflow: Optional[OrderFlowState]
    context: Optional[ContextGraphState]
    regimes: RegimeProbabilities
    dominant_regime: Optional[str]
    timeframe_conflict_score: Decimal
    uncertainty: UncertaintyState
    strategic_bias: str
    tactical_state: str
    execution_ready: bool
    no_trade: bool
    reason_codes: tuple[str, ...]
    feature_vector: Mapping[str, float]
    metadata: Mapping[str, Any] = field(default_factory=dict)
