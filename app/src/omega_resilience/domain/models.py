from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Mapping, Any, Optional

class ServiceClass(str, Enum):
    CRITICAL = "CRITICAL"
    IMPORTANT = "IMPORTANT"
    NONCRITICAL = "NONCRITICAL"

class HealthState(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

class RecoveryState(str, Enum):
    BOOT = "BOOT"
    SELF_TEST = "SELF_TEST"
    BROKER_CONNECT = "BROKER_CONNECT"
    ACCOUNT_SYNC = "ACCOUNT_SYNC"
    POSITION_SYNC = "POSITION_SYNC"
    ORDER_SYNC = "ORDER_SYNC"
    DATABASE_RECONCILIATION = "DATABASE_RECONCILIATION"
    RISK_REBUILD = "RISK_REBUILD"
    MARKET_DATA_HEALTH = "MARKET_DATA_HEALTH"
    SAFE = "SAFE"
    READY = "READY"
    LIVE = "LIVE"
    PAUSED = "PAUSED"
    CAUTION = "CAUTION"
    DEFENSIVE = "DEFENSIVE"
    RECOVERY = "RECOVERY"
    EMERGENCY = "EMERGENCY"
    SHUTDOWN = "SHUTDOWN"

class IncidentSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    BLOCKING = "BLOCKING"
    CRITICAL = "CRITICAL"

@dataclass(frozen=True, slots=True)
class ServiceDescriptor:
    service_id: str
    service_class: ServiceClass
    dependencies: tuple[str, ...]
    auto_restart_allowed: bool
    restart_requires_safe: bool

@dataclass(frozen=True, slots=True)
class Heartbeat:
    service_id: str
    instance_id: str
    counter: int
    sent_at: datetime
    health: HealthState
    last_successful_work_at: datetime
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class ResourceSnapshot:
    captured_at: datetime
    cpu_pct: Decimal
    memory_pct: Decimal
    disk_free_pct: Decimal
    disk_free_gb: Decimal
    temperature_c: Optional[Decimal]
    load_1m: Optional[Decimal] = None

@dataclass(frozen=True, slots=True)
class NetworkSnapshot:
    captured_at: datetime
    target: str
    reachable: bool
    latency_ms: Optional[Decimal]
    packet_loss_pct: Decimal

@dataclass(frozen=True, slots=True)
class ClockSnapshot:
    captured_at: datetime
    synchronized: bool
    offset_ms: Decimal
    source: str

@dataclass(frozen=True, slots=True)
class ReconciliationResult:
    accounts_ok: bool
    positions_ok: bool
    orders_ok: bool
    balances_ok: bool
    database_ok: bool
    reason_codes: tuple[str, ...] = ()

@dataclass(frozen=True, slots=True)
class BackupRecord:
    backup_id: str
    created_at: datetime
    path: str
    checksum_sha256: str
    verified_at: Optional[datetime]
    restore_tested_at: Optional[datetime]
    restore_test_passed: bool
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class Incident:
    incident_id: str
    fingerprint: str
    severity: IncidentSeverity
    category: str
    affected_services: tuple[str, ...]
    started_at: datetime
    last_seen_at: datetime
    occurrence_count: int
    reason_codes: tuple[str, ...]
    message_ru: str
    resolved_at: Optional[datetime] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class SelfAuditCheck:
    key: str
    passed: bool
    blocking: bool
    reason_codes: tuple[str, ...]
    message_ru: str

@dataclass(frozen=True, slots=True)
class SelfAuditReport:
    created_at: datetime
    checks: tuple[SelfAuditCheck, ...]
    passed: bool
    ready_allowed: bool
    reason_codes: tuple[str, ...]
