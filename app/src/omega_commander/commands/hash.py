from __future__ import annotations
from dataclasses import asdict
from datetime import datetime
from enum import Enum
from uuid import UUID
import hashlib, json

def _norm(x):
    if isinstance(x, dict):
        return {str(k): _norm(v) for k,v in sorted(x.items(), key=lambda kv: str(kv[0]))}
    if isinstance(x, (list,tuple)):
        return [_norm(v) for v in x]
    if isinstance(x, datetime):
        return x.isoformat()
    if isinstance(x, UUID):
        return str(x)
    if isinstance(x, Enum):
        return x.value
    if hasattr(x, "__dataclass_fields__"):
        return _norm(asdict(x))
    return x

def command_hash(command) -> str:
    # State intentionally excluded from semantic identity.
    payload = {
        "command_id": command.command_id,
        "command_type": command.command_type,
        "requested_at": command.requested_at,
        "principal_id": command.principal.principal_id,
        "role": command.principal.role,
        "target": command.target,
        "params": command.params,
        "correlation_id": command.correlation_id,
        "idempotency_key": command.idempotency_key,
    }
    raw=json.dumps(_norm(payload),sort_keys=True,separators=(",",":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
