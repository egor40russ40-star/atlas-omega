from __future__ import annotations
from dataclasses import asdict, is_dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID
import hashlib, json


def _norm(x):
    if is_dataclass(x): return _norm(asdict(x))
    if isinstance(x,dict): return {str(k):_norm(v) for k,v in sorted(x.items(),key=lambda kv:str(kv[0]))}
    if isinstance(x,(list,tuple,set)): return [_norm(v) for v in x]
    if isinstance(x,Decimal): return format(x,"f")
    if isinstance(x,datetime): return x.isoformat()
    if isinstance(x,UUID): return str(x)
    if isinstance(x,Enum): return x.value
    return x


def canonical_hash(value) -> str:
    raw=json.dumps(_norm(value),ensure_ascii=False,sort_keys=True,separators=(",",":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
