from __future__ import annotations
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from omega_execution.domain.models import InstrumentRules

def normalize_price(price: Decimal, rules: InstrumentRules) -> Decimal:
    if price <= 0:
        raise ValueError("price must be positive")
    steps = (price / rules.price_step).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return steps * rules.price_step

def normalize_quantity(quantity: Decimal, rules: InstrumentRules) -> Decimal:
    if quantity <= 0:
        raise ValueError("quantity must be positive")
    steps = (quantity / rules.quantity_step).quantize(Decimal("1"), rounding=ROUND_DOWN)
    q = steps * rules.quantity_step
    if q < rules.min_quantity:
        raise ValueError("EXEC_QUANTITY_NOT_NORMALIZED")
    return q

def validate_normalized_price(price: Decimal | None, rules: InstrumentRules) -> None:
    if price is None:
        return
    if normalize_price(price, rules) != price:
        raise ValueError("EXEC_PRICE_NOT_NORMALIZED")

def validate_normalized_quantity(quantity: Decimal, rules: InstrumentRules) -> None:
    if normalize_quantity(quantity, rules) != quantity:
        raise ValueError("EXEC_QUANTITY_NOT_NORMALIZED")
