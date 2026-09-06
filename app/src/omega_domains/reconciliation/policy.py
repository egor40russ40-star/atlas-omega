from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

BLOCKING = {"BLOCKING", "CRITICAL"}

def overall_status(statuses: Iterable[str]) -> str:
    values = set(statuses)
    if "CRITICAL" in values:
        return "CRITICAL"
    if "BLOCKING" in values:
        return "BLOCKING"
    if "WARNING" in values:
        return "WARNING"
    return "OK"

def trading_must_be_blocked(status: str) -> bool:
    return status in BLOCKING
