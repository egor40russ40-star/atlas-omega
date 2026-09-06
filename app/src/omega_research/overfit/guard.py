from __future__ import annotations
from decimal import Decimal
from omega_research.domain.models import OverfitEvidence, OverfitDecision

def evaluate_overfit(
    evidence: OverfitEvidence,
    *,
    minimum_trades: int = 30,
    minimum_walkforward_folds: int = 3,
    max_best_fold_profit_share: Decimal = Decimal("0.60"),
    minimum_cost_robustness_ratio: Decimal = Decimal("0.70"),
    minimum_neighbour_parameter_pass_rate: Decimal = Decimal("0.60"),
) -> OverfitDecision:
    reasons=[]
    if evidence.trades < minimum_trades:
        reasons.append("RESEARCH_OVERFIT_SAMPLE_TOO_SMALL")
    if evidence.walkforward_folds < minimum_walkforward_folds:
        reasons.append("RESEARCH_OVERFIT_SAMPLE_TOO_SMALL")
    if evidence.best_fold_profit_share > max_best_fold_profit_share:
        reasons.append("RESEARCH_OVERFIT_SINGLE_FOLD_DEPENDENCY")
    if evidence.cost_robustness_ratio < minimum_cost_robustness_ratio:
        reasons.append("RESEARCH_OVERFIT_COST_FRAGILE")
    if evidence.neighbour_parameter_pass_rate < minimum_neighbour_parameter_pass_rate:
        reasons.append("RESEARCH_OVERFIT_PARAMETER_FRAGILE")
    if evidence.leakage_violations > 0:
        reasons.append("RESEARCH_LEAKAGE_DETECTED")
    if not evidence.reproducible:
        reasons.append("RESEARCH_LEAKAGE_DETECTED")
    return OverfitDecision(not reasons,tuple(sorted(set(reasons))))
