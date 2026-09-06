from __future__ import annotations
import hashlib, json
from dataclasses import asdict, is_dataclass
from decimal import Decimal

def _normalize(obj):
    if is_dataclass(obj):
        obj = asdict(obj)
    if isinstance(obj, dict):
        return {str(k): _normalize(v) for k, v in sorted(obj.items(), key=lambda x: str(x[0]))}
    if isinstance(obj, (list, tuple)):
        return [_normalize(v) for v in obj]
    if isinstance(obj, Decimal):
        return format(obj, "f")
    return obj

def make_policy_hash(policy) -> str:
    raw = json.dumps(_normalize(policy), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
