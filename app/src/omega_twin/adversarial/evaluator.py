from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping
from omega_twin.scenarios.faults import StressScenario

@dataclass(frozen=True, slots=True)
class ScenarioResult:
    scenario_name: str
    passed: bool
    expectancy_r_after_costs: Decimal
    max_drawdown_r: Decimal
    safety_violations: int
    catastrophic_failure: bool
    reason_codes: tuple[str,...]

def evaluate_scenario(
    scenario: StressScenario,
    *,
    expectancy_r_after_costs: Decimal,
    max_drawdown_r: Decimal,
    safety_violations: int,
    catastrophic_failure: bool,
    max_allowed_drawdown_r: Decimal | None = None,
) -> ScenarioResult:
    reasons=[]
    if safety_violations:
        reasons.append("TWIN_SAFETY_VIOLATION")
    if catastrophic_failure:
        reasons.append("TWIN_ADVERSARIAL_FAILURE")
    if max_allowed_drawdown_r is not None and max_drawdown_r > max_allowed_drawdown_r:
        reasons.append("TWIN_DRAWDOWN_EXCESSIVE")
    passed = not reasons
    return ScenarioResult(
        scenario.name,passed,expectancy_r_after_costs,max_drawdown_r,
        safety_violations,catastrophic_failure,tuple(sorted(set(reasons)))
    )

def pass_rate(results) -> Decimal:
    rows=list(results)
    if not rows:
        return Decimal("0")
    return Decimal(sum(r.passed for r in rows))/Decimal(len(rows))
