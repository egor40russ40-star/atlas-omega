from __future__ import annotations
import hashlib, json
from dataclasses import asdict, replace
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from omega_data.domain.models import EventEnvelope

def _norm(v):
    if isinstance(v, dict):
        return {str(k): _norm(val) for k, val in sorted(v.items(), key=lambda x: str(x[0]))}
    if isinstance(v, (list, tuple)):
        return [_norm(x) for x in v]
    if isinstance(v, Decimal):
        return format(v, "f")
    if isinstance(v, datetime):
        return v.isoformat()
    if isinstance(v, UUID):
        return str(v)
    if hasattr(v, "__dataclass_fields__"):
        return _norm(asdict(v))
    return v

def payload_hash(payload) -> str:
    raw = json.dumps(_norm(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def with_payload_hash(event: EventEnvelope) -> EventEnvelope:
    return replace(event, payload_hash=payload_hash(event.payload))
