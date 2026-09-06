from __future__ import annotations
import re
from typing import Any

SECRET_KEYS = (
    "token","password","secret","authorization","api_key","access_token","refresh_token"
)

def redact_mapping(value: Any):
    if isinstance(value,dict):
        out={}
        for k,v in value.items():
            if any(s in str(k).lower() for s in SECRET_KEYS):
                out[k]="***REDACTED***" if v is not None else None
            else:
                out[k]=redact_mapping(v)
        return out
    if isinstance(value,list):
        return [redact_mapping(v) for v in value]
    if isinstance(value,tuple):
        return tuple(redact_mapping(v) for v in value)
    return value

def valid_secret_reference(ref: str | None) -> bool:
    if ref is None:
        return True
    return ref.startswith("env:") and len(ref) > 4

def suspicious_secret_assignment(text: str) -> bool:
    patterns=[
        r'(?i)(token|password|api[_-]?key|secret)\s*[:=]\s*["\'][A-Za-z0-9_\-\.]{16,}["\']',
        r'(?i)authorization\s*[:=]\s*["\']Bearer\s+[A-Za-z0-9_\-\.]{16,}["\']',
    ]
    return any(re.search(p,text) for p in patterns)
