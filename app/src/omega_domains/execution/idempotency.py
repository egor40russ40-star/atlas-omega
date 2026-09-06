from __future__ import annotations
import hashlib, json
from typing import Any
from omega_common.decimal import canonical_decimal


def make_idempotency_key(
    *, intent_id: str, broker_account_id: str, instrument_id: str, side: str,
    quantity: Any, order_style: str, limit_price: Any | None, stop_price: Any | None,
    approval_chain_hash: str,
) -> str:
    canonical={
        "intent_id":intent_id,
        "broker_account_id":broker_account_id,
        "instrument_id":instrument_id,
        "side":side,
        "quantity":canonical_decimal(quantity),
        "order_style":order_style,
        "limit_price":canonical_decimal(limit_price),
        "stop_price":canonical_decimal(stop_price),
        "approval_chain_hash":approval_chain_hash,
    }
    raw=json.dumps(canonical,ensure_ascii=False,sort_keys=True,separators=(",",":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
