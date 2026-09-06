from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4
import hashlib, json

@dataclass(frozen=True, slots=True)
class SafetyAuthorization:
    authorization_id: UUID
    intent_id: UUID
    account_id: str
    instrument_id: str
    side: str
    quantity: Decimal
    order_style: str
    limit_price: Decimal | None
    capital_decision_hash: str
    risk_decision_hash: str
    market_snapshot_id: str
    broker_state_snapshot_id: str
    issued_at: datetime
    valid_until: datetime
    authorization_hash: str

def _canonical_payload(
    *,
    intent_id: UUID,
    account_id: str,
    instrument_id: str,
    side: str,
    quantity: Decimal,
    order_style: str,
    limit_price: Decimal | None,
    capital_decision_hash: str,
    risk_decision_hash: str,
    market_snapshot_id: str,
    broker_state_snapshot_id: str,
    issued_at: datetime,
    valid_until: datetime,
) -> dict:
    return {
        "intent_id": str(intent_id),
        "account_id": account_id,
        "instrument_id": instrument_id,
        "side": side,
        "quantity": format(quantity, "f"),
        "order_style": order_style,
        "limit_price": None if limit_price is None else format(limit_price, "f"),
        "capital_decision_hash": capital_decision_hash,
        "risk_decision_hash": risk_decision_hash,
        "market_snapshot_id": market_snapshot_id,
        "broker_state_snapshot_id": broker_state_snapshot_id,
        "issued_at": issued_at.isoformat(),
        "valid_until": valid_until.isoformat(),
    }

def _hash(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def issue_authorization(**kwargs) -> SafetyAuthorization:
    payload = _canonical_payload(**kwargs)
    return SafetyAuthorization(
        authorization_id=uuid4(),
        authorization_hash=_hash(payload),
        **kwargs,
    )

def validate_authorization(auth: SafetyAuthorization, *, now: datetime | None = None) -> list[str]:
    now = now or datetime.now(timezone.utc)
    reasons: list[str] = []
    payload = _canonical_payload(
        intent_id=auth.intent_id,
        account_id=auth.account_id,
        instrument_id=auth.instrument_id,
        side=auth.side,
        quantity=auth.quantity,
        order_style=auth.order_style,
        limit_price=auth.limit_price,
        capital_decision_hash=auth.capital_decision_hash,
        risk_decision_hash=auth.risk_decision_hash,
        market_snapshot_id=auth.market_snapshot_id,
        broker_state_snapshot_id=auth.broker_state_snapshot_id,
        issued_at=auth.issued_at,
        valid_until=auth.valid_until,
    )
    if _hash(payload) != auth.authorization_hash:
        reasons.append("RISK_APPROVAL_HASH_MISMATCH")
    if auth.valid_until <= now:
        reasons.append("RISK_APPROVAL_EXPIRED")
    return sorted(set(reasons))
