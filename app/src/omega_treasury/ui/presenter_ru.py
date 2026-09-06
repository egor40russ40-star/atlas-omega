from __future__ import annotations
from decimal import Decimal

def money(v: Decimal, currency: str = "₽") -> str:
    q = v.quantize(Decimal("0.01"))
    return f"{q:,.2f} {currency}".replace(",", " ")

def account_summary_ru(
    *,
    name: str,
    own_funds: Decimal,
    borrowed_funds: Decimal,
    free_capital: Decimal,
    reserved: Decimal,
    deployed: Decimal,
) -> str:
    return "\n".join([
        f"Счёт: {name}",
        f"Собственные средства: {money(own_funds)}",
        f"Заёмные средства: {money(borrowed_funds)}",
        f"Свободный капитал: {money(free_capital)}",
        f"Зарезервировано заявками: {money(reserved)}",
        f"Задействовано в позициях: {money(deployed)}",
    ])
