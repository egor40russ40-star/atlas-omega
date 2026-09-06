from __future__ import annotations
from dataclasses import asdict
from decimal import Decimal
import hashlib,json

def _norm(x):
    if isinstance(x,dict):
        return {str(k):_norm(v) for k,v in sorted(x.items(),key=lambda kv:str(kv[0]))}
    if isinstance(x,(list,tuple)):
        return [_norm(v) for v in x]
    if isinstance(x,Decimal):
        return format(x,"f")
    return x

def genome_hash(genome) -> str:
    raw=json.dumps(_norm(asdict(genome)),sort_keys=True,separators=(",",":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
