from __future__ import annotations
from dataclasses import asdict, replace
from decimal import Decimal
from datetime import datetime
from enum import Enum
from uuid import UUID
import json, hashlib
from omega_twin.domain.models import ExperimentManifest

def _norm(x):
    if isinstance(x,dict):
        return {str(k):_norm(v) for k,v in sorted(x.items(),key=lambda kv:str(kv[0]))}
    if isinstance(x,(list,tuple)):
        return [_norm(v) for v in x]
    if isinstance(x,Decimal):
        return format(x,"f")
    if isinstance(x,datetime):
        return x.isoformat()
    if isinstance(x,UUID):
        return str(x)
    if isinstance(x,Enum):
        return x.value
    return x

def manifest_hash(m: ExperimentManifest) -> str:
    raw=json.dumps(_norm(asdict(m)),ensure_ascii=False,sort_keys=True,separators=(",",":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def verify_manifest(m: ExperimentManifest, expected_hash: str) -> bool:
    return manifest_hash(m)==expected_hash
