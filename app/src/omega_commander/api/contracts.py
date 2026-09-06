from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping,Any

@dataclass(frozen=True, slots=True)
class ApiEnvelope:
    ok: bool
    data: Mapping[str,Any] | None
    reason_codes: tuple[str,...]
    message_ru: str

READ_ENDPOINTS = (
    "/api/v1/status",
    "/api/v1/market",
    "/api/v1/accounts",
    "/api/v1/positions",
    "/api/v1/orders",
    "/api/v1/strategies",
    "/api/v1/risk",
    "/api/v1/performance",
    "/api/v1/research",
    "/api/v1/computer",
    "/api/v1/incidents",
    "/api/v1/journal",
)

WRITE_ENDPOINTS = (
    "/api/v1/commands",
    "/api/v1/confirmations",
)

FORBIDDEN_DIRECT_ENDPOINTS = (
    "/api/v1/broker/order",
    "/api/v1/risk/disable",
    "/api/v1/safety/disable",
)
