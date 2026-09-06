from __future__ import annotations
from decimal import Decimal, InvalidOperation
from typing import TypeAlias, Any

Money: TypeAlias = Decimal
Price: TypeAlias = Decimal
Quantity: TypeAlias = Decimal
Ratio: TypeAlias = Decimal


def as_decimal(value: Any, *, field: str = "value") -> Decimal:
    """Convert a boundary value without binary-float arithmetic in domain logic."""
    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool):
        raise TypeError(f"{field} must be numeric, not bool")
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise TypeError(f"{field} must be decimal-compatible") from exc


def optional_decimal(value: Any | None, *, field: str = "value") -> Decimal | None:
    return None if value is None else as_decimal(value, field=field)


def canonical_decimal(value: Any | None) -> str | None:
    if value is None:
        return None
    d=as_decimal(value)
    if d == 0:
        return "0"
    text=format(d.normalize(),"f")
    return text.rstrip("0").rstrip(".") if "." in text else text
