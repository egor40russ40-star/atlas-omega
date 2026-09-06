from __future__ import annotations
from omega_resilience.domain.models import SelfAuditCheck

def bool_check(key: str, ok: bool, *, blocking: bool, fail_code: str, ok_message: str, fail_message: str):
    return SelfAuditCheck(
        key,ok,blocking,() if ok else (fail_code,),ok_message if ok else fail_message
    )
