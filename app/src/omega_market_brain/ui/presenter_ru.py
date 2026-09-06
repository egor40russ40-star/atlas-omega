from __future__ import annotations
from omega_market_brain.domain.models import WorldModelSnapshot

def world_model_summary_ru(m: WorldModelSnapshot) -> str:
    lines = [
        f"{m.instrument_id} — MARKET BRAIN",
        f"Стратегическое направление: {m.strategic_bias}",
        f"Тактическое состояние: {'ГОТОВ' if m.tactical_state == 'READY' else 'ОЖИДАНИЕ'}",
        f"Исполнение на младшем ТФ: {'готово' if m.execution_ready else 'не подтверждено'}",
        f"Доминирующий режим: {m.dominant_regime or 'не определён'}",
        f"Конфликт таймфреймов: {float(m.timeframe_conflict_score)*100:.1f}%",
        f"Неопределённость: {m.uncertainty.level.value} ({float(m.uncertainty.score)*100:.1f}%)",
        f"Новая сделка: {'НЕ РЕКОМЕНДУЕТСЯ' if m.no_trade else 'может оцениваться стратегиями'}",
    ]
    if m.reason_codes:
        lines.append("Причины/оговорки:")
        lines.extend(f"- {x}" for x in m.reason_codes)
    return "\n".join(lines)
