from __future__ import annotations
from omega_research.domain.models import OverfitDecision, StrategyCandidate

def candidate_summary_ru(candidate: StrategyCandidate) -> str:
    return "\n".join([
        f"Кандидат: {candidate.candidate_id}",
        f"Семейство: {candidate.family}",
        f"Поколение: {candidate.generation}",
        f"Состояние: {candidate.state.value}",
        f"Изменений: {len(candidate.changes)}",
        "LIVE-разрешение: НЕТ",
        "Следующий этап: Digital Twin / Validation Lab",
    ])

def overfit_report_ru(d: OverfitDecision) -> str:
    if d.passed:
        return "Anti-overfitting: ПРОЙДЕН. Кандидат может быть передан в Validation."
    lines=["Anti-overfitting: НЕ ПРОЙДЕН.","Причины:"]
    lines.extend(f"- {x}" for x in d.reason_codes)
    return "\n".join(lines)
