from __future__ import annotations
from omega_strategy.domain.models import RouterDecision

def router_decision_ru(d: RouterDecision) -> str:
    if d.action == "WAIT":
        lines=["META ROUTER: ОЖИДАНИЕ"]
    else:
        lines=[
            f"META ROUTER: {d.action}",
            f"Стратегия: {d.selected_strategy_id}",
            f"Итоговый score: {float(d.final_score)*100:.1f}%",
            f"Кандидат на LIVE: {'ДА' if d.live_candidate else 'НЕТ'}",
        ]
    if d.reason_codes:
        lines.append("Причины:")
        lines.extend(f"- {x}" for x in d.reason_codes)
    return "\n".join(lines)
