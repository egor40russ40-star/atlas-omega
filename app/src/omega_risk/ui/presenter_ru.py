from __future__ import annotations
from decimal import Decimal

def money(v: Decimal) -> str:
    return f"{v.quantize(Decimal('0.01')):,.2f} ₽".replace(",", " ")

def risk_decision_ru(status: str, requested: Decimal, approved: Decimal, reasons: tuple[str, ...]) -> str:
    head = {
        "APPROVED": "РИСК РАЗРЕШЁН",
        "REDUCED": "РИСК УМЕНЬШЕН",
        "DENIED": "СДЕЛКА ПО РИСКУ ЗАПРЕЩЕНА",
    }.get(status, status)

    lines = [
        head,
        f"Запрошенный риск: {money(requested)}",
        f"Разрешённый риск: {money(approved)}",
    ]
    if reasons:
        lines.append("Причины:")
        for r in reasons:
            lines.append(f"- {r}")
    return "\n".join(lines)
