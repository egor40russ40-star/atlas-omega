from __future__ import annotations
from decimal import Decimal
from omega_twin.domain.models import (
    ValidationMetrics, PromotionReport, PromotionDecision
)

def promotion_report(
    *,
    challenger_id: str,
    champion_id: str | None,
    metrics: ValidationMetrics,
    walkforward_folds: int,
    minimum_walkforward_folds: int,
    minimum_trades: int,
    monte_carlo_p95_drawdown_r: Decimal | None,
    max_monte_carlo_p95_drawdown_r: Decimal | None,
    adversarial_pass_rate: Decimal,
    minimum_adversarial_pass_rate: Decimal,
    shadow_samples: int,
    minimum_shadow_samples: int,
    sandbox_samples: int,
    minimum_sandbox_samples: int,
    reproducible: bool,
) -> PromotionReport:
    reasons=[]

    if not reproducible:
        reasons.append("TWIN_MANIFEST_HASH_MISMATCH")
    if metrics.trades < minimum_trades:
        reasons.append("TWIN_SAMPLE_TOO_SMALL")
    if walkforward_folds < minimum_walkforward_folds:
        reasons.append("TWIN_WALKFORWARD_INSUFFICIENT_FOLDS")
    if metrics.expectancy_r_after_costs <= 0:
        reasons.append("TWIN_EXPECTANCY_NONPOSITIVE")
    if metrics.safety_violations > 0:
        reasons.append("TWIN_SAFETY_VIOLATION")
    if (
        monte_carlo_p95_drawdown_r is not None
        and max_monte_carlo_p95_drawdown_r is not None
        and monte_carlo_p95_drawdown_r > max_monte_carlo_p95_drawdown_r
    ):
        reasons.append("TWIN_MONTE_CARLO_RISK_HIGH")
    if adversarial_pass_rate < minimum_adversarial_pass_rate:
        reasons.append("TWIN_ADVERSARIAL_FAILURE")
    if shadow_samples < minimum_shadow_samples:
        reasons.append("TWIN_SHADOW_EVIDENCE_MISSING")
    if sandbox_samples < minimum_sandbox_samples:
        reasons.append("TWIN_SANDBOX_EVIDENCE_MISSING")

    decision=PromotionDecision.PASS if not reasons else PromotionDecision.FAIL
    if decision is PromotionDecision.PASS:
        reasons.append("TWIN_PROMOTION_PASS")

    return PromotionReport(
        challenger_id,champion_id,decision,tuple(sorted(set(reasons))),
        metrics,walkforward_folds,monte_carlo_p95_drawdown_r,
        adversarial_pass_rate,shadow_samples,sandbox_samples,reproducible
    )
