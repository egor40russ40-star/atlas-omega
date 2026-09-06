from __future__ import annotations
from omega_memory.wait_learning.statistics import FilterStats
from omega_memory.analytics.similarity_summary import SimilarityOutcomeSummary

def filter_stats_ru(s: FilterStats) -> str:
    lines=[
        f"Фильтр: {s.reason_code}",
        f"Оценённых WAIT: {s.evaluable_waits}",
        f"Предотвращено плохих сценариев: {s.avoided_bad}",
        f"Пропущено хороших сценариев: {s.missed_good}",
        f"Нейтральных: {s.neutral}",
        f"Полезность (исследовательская): {float(s.utility_score):+.3f}",
    ]
    if "MEMORY_FILTER_SAMPLE_TOO_SMALL" in s.reason_codes:
        lines.append("Вывод: выборка пока мала — решение менять фильтр преждевременно.")
    elif s.utility_score > 0:
        lines.append("Вывод: фильтр чаще защищал от плохих сценариев, чем мешал.")
    elif s.utility_score < 0:
        lines.append("Вывод: фильтр может быть слишком строгим; требуется Validation.")
    else:
        lines.append("Вывод: выраженного преимущества фильтра пока нет.")
    return "\n".join(lines)

def similarity_summary_ru(s: SimilarityOutcomeSummary) -> str:
    if s.support_count == 0:
        return "Похожие состояния: недостаточно данных."
    return "\n".join([
        f"Похожих состояний с полным исходом: {s.support_count}",
        f"Положительный исход: {float(s.positive_rate or 0)*100:.1f}%",
        f"Отрицательный исход: {float(s.negative_rate or 0)*100:.1f}%",
        f"Медианный результат: {float(s.median_return_pct or 0)*100:+.3f}%",
    ])
