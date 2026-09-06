from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Mapping, Any, Optional
from uuid import UUID

class Role(str, Enum):
    VIEWER = "VIEWER"
    OPERATOR = "OPERATOR"
    ADMIN = "ADMIN"
    SYSTEM = "SYSTEM"

class ClientType(str, Enum):
    LOCAL_WEB = "LOCAL_WEB"
    MOBILE_WEB = "MOBILE_WEB"
    SYSTEM = "SYSTEM"

class CommandType(str, Enum):
    SAFE_PAUSE = "SAFE_PAUSE"
    ENTER_SAFE = "ENTER_SAFE"
    EMERGENCY_STOP = "EMERGENCY_STOP"
    RESUME_TRADING = "RESUME_TRADING"
    ACK_INCIDENT = "ACK_INCIDENT"
    RESTART_NONCRITICAL_SERVICE = "RESTART_NONCRITICAL_SERVICE"
    RESTART_CRITICAL_SERVICE = "RESTART_CRITICAL_SERVICE"
    UPDATE_OPERATIONAL_SETTING = "UPDATE_OPERATIONAL_SETTING"
    DISABLE_RISK_GOVERNOR = "DISABLE_RISK_GOVERNOR"
    DISABLE_SAFETY_KERNEL = "DISABLE_SAFETY_KERNEL"
    BYPASS_RECONCILIATION = "BYPASS_RECONCILIATION"
    DIRECT_BROKER_ORDER = "DIRECT_BROKER_ORDER"
    DELETE_FINANCIAL_AUDIT = "DELETE_FINANCIAL_AUDIT"
    FORCE_LIVE_UNVERIFIED_STRATEGY = "FORCE_LIVE_UNVERIFIED_STRATEGY"

class CommandState(str, Enum):
    DRAFT = "DRAFT"
    AWAITING_CONFIRMATION = "AWAITING_CONFIRMATION"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    DENIED = "DENIED"
    FAILED = "FAILED"

@dataclass(frozen=True, slots=True)
class Principal:
    principal_id: str
    role: Role
    client_type: ClientType
    authenticated_at: datetime

@dataclass(frozen=True, slots=True)
class CommanderCommand:
    command_id: UUID
    command_type: CommandType
    requested_at: datetime
    principal: Principal
    target: Optional[str]
    params: Mapping[str, Any]
    correlation_id: UUID
    idempotency_key: str
    state: CommandState = CommandState.DRAFT

@dataclass(frozen=True, slots=True)
class ConfirmationChallenge:
    confirmation_id: UUID
    command_id: UUID
    command_hash: str
    issued_at: datetime
    expires_at: datetime
    nonce: str
    human_summary_ru: str
    consequences_ru: tuple[str, ...]

@dataclass(frozen=True, slots=True)
class CommandDecision:
    allowed: bool
    requires_confirmation: bool
    reason_codes: tuple[str, ...]

@dataclass(frozen=True, slots=True)
class CommandResult:
    command_id: UUID
    state: CommandState
    reason_codes: tuple[str, ...]
    message_ru: str
    system_state_before: str
    system_state_after: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class SystemStatus:
    captured_at: datetime
    operational_state: str
    crisis_mode: str
    broker_connected: bool
    reconciliation_status: str
    market_data_fresh: bool
    kill_switch_active: bool
    safe_pause_active: bool
    daily_pnl_rub: str
    open_risk_rub: str
    positions_count: int
    active_orders_count: int
    critical_incidents: int
    cpu_pct: float
    memory_pct: float
    disk_free_gb: float
    metadata: Mapping[str, Any] = field(default_factory=dict)
