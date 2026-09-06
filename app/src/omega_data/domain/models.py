from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Mapping, Optional
from uuid import UUID

class StorageTier(str, Enum):
    HOT = "HOT"
    WARM = "WARM"
    ARCHIVE = "ARCHIVE"

class DataClass(str, Enum):
    CRITICAL_FINANCIAL = "CRITICAL_FINANCIAL"
    BLACKBOX_CRITICAL = "BLACKBOX_CRITICAL"
    BLACKBOX_NORMAL = "BLACKBOX_NORMAL"
    MARKET_RAW = "MARKET_RAW"
    MARKET_AGGREGATED = "MARKET_AGGREGATED"
    RESEARCH_INTERMEDIATE = "RESEARCH_INTERMEDIATE"
    RESEARCH_RESULT = "RESEARCH_RESULT"
    TEMPORARY = "TEMPORARY"

class SegmentState(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    QUARANTINED = "QUARANTINED"
    SUPERSEDED = "SUPERSEDED"
    DELETED = "DELETED"

@dataclass(frozen=True, slots=True)
class DataQuality:
    score: float
    freshness: float
    completeness: float
    sequence_integrity: float
    source_health: float
    timestamp_integrity: float
    reason_codes: tuple[str, ...] = ()

@dataclass(frozen=True, slots=True)
class EventEnvelope:
    event_id: UUID
    event_type: str
    schema_version: int
    occurred_at: datetime
    received_at: datetime
    source: str
    payload: Mapping[str, Any]
    correlation_id: Optional[UUID] = None
    causation_id: Optional[UUID] = None
    account_id: Optional[str] = None
    instrument_id: Optional[str] = None
    strategy_id: Optional[str] = None
    market_snapshot_id: Optional[str] = None
    sequence: Optional[int] = None
    quality: Optional[DataQuality] = None
    payload_hash: Optional[str] = None

@dataclass(frozen=True, slots=True)
class ArchiveSegment:
    segment_id: UUID
    stream: str
    instrument_id: Optional[str]
    date_key: str
    tier: StorageTier
    data_class: DataClass
    path: str
    state: SegmentState
    checksum: Optional[str]
    row_count: int
    min_occurred_at: Optional[datetime]
    max_occurred_at: Optional[datetime]
    metadata: Mapping[str, Any] = field(default_factory=dict)
