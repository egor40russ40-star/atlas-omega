from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Mapping, Any

class DeploymentMode(str, Enum):
    OFFLINE_FAKE = "OFFLINE_FAKE"
    SANDBOX = "SANDBOX"
    SHADOW = "SHADOW"
    LIVE = "LIVE"

class NodeRole(str, Enum):
    RESEARCH_NODE = "RESEARCH_NODE"
    LIVE_NODE = "LIVE_NODE"

class CheckState(str, Enum):
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"

class SandboxRunState(str, Enum):
    CREATED = "CREATED"
    PREFLIGHT = "PREFLIGHT"
    BOOTING = "BOOTING"
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

@dataclass(frozen=True, slots=True)
class PreflightCheck:
    key: str
    state: CheckState
    message_ru: str
    reason_codes: tuple[str,...] = ()
    details: Mapping[str,Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class PreflightReport:
    created_at: datetime
    checks: tuple[PreflightCheck,...]
    passed: bool
    blocking_reason_codes: tuple[str,...]

@dataclass(frozen=True, slots=True)
class RuntimeConfig:
    node_role: NodeRole
    mode: DeploymentMode
    runtime_dir: str
    data_dir: str
    logs_dir: str
    sandbox_db: str
    broker_adapter: str
    broker_network_enabled: bool
    broker_secret_ref: str | None
    live_enabled: bool
    live_hard_locked: bool
    execution_process_enabled: bool
    broker_write_enabled: bool
    broker_token_allowed: bool
    production_db_write_enabled: bool
    research_enabled: bool
    data_access: str
    commander_bind: str
    remote_access: str
    metadata: Mapping[str,Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class SandboxRunResult:
    run_id: str
    instrument_id: str
    state: SandboxRunState
    stage: str
    execution_state: str | None
    broker_order_id: str | None
    reason_codes: tuple[str,...]
    message_ru: str
    metadata: Mapping[str,Any] = field(default_factory=dict)
