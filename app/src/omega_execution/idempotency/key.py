from __future__ import annotations
import hashlib, json
from decimal import Decimal

def make_key(
    *,
    intent_id: str,
    broker_account_id: str,
    instrument_id: str,
    side: str,
    quantity: Decimal,
    order_style: str,
    limit_price: Decimal | None,
    stop_price: Decimal | None,
    approval_chain_hash: str,
) -> str:
    payload = {
        "intent_id": intent_id,
        "broker_account_id": broker_account_id,
        "instrument_id": instrument_id,
        "side": side,
        "quantity": format(quantity, "f"),
        "order_style": order_style,
        "limit_price": None if limit_price is None else format(limit_price, "f"),
        "stop_price": None if stop_price is None else format(stop_price, "f"),
        "approval_chain_hash": approval_chain_hash,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
