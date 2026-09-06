from __future__ import annotations
from omega_twin.domain.models import PromotionReport

def promotion_report_ru(r: PromotionReport) -> str:
    lines=[
        f"CHALLENGER: {r.challenger_id}",
        f"CHAMPION: {r.champion_id or 'нет'}",
        f"РЕШЕНИЕ: {r.decision.value}",
        f"Сделок: {r.metrics.trades}",
        f"Ожидание после расходов: {float(r.metrics.expectancy_r_after_costs):+.3f} R",
        f"Макс. просадка: {float(r.metrics.max_drawdown_r):.3f} R",
        f"Макс. серия убытков: {r.metrics.max_consecutive_losses}",
        f"Walk-forward folds: {r.walkforward_folds}",
        f"Adversarial pass rate: {float(r.adversarial_pass_rate)*100:.1f}%",
        f"Shadow samples: {r.shadow_samples}",
        f"Sandbox samples: {r.sandbox_samples}",
        f"Воспроизводимость: {'ДА' if r.reproducible else 'НЕТ'}",
    ]
    if r.monte_carlo_p95_drawdown_r is not None:
        lines.append(f"Monte Carlo p95 drawdown: {float(r.monte_carlo_p95_drawdown_r):.3f} R")
    if r.reason_codes:
        lines.append("Причины:")
        lines.extend(f"- {x}" for x in r.reason_codes)
    return "\n".join(lines)
