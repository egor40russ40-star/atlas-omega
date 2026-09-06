from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from omega_twin.domain.models import ValidationMetrics

@dataclass(frozen=True, slots=True)
class Scorecard:
    challenger_score: Decimal
    champion_score: Decimal | None
    improvement: Decimal | None
    reason_codes: tuple[str,...]

def _score(m: ValidationMetrics) -> Decimal:
    # Research score only, not a probability.
    expectancy=max(min(m.expectancy_r_after_costs,Decimal("2")),Decimal("-2"))
    dd_penalty=min(m.max_drawdown_r,Decimal("10"))/Decimal("10")
    loss_streak_penalty=min(Decimal(m.max_consecutive_losses),Decimal("10"))/Decimal("10")
    safety_penalty=Decimal("1") if m.safety_violations else Decimal("0")
    raw = Decimal("0.5") + expectancy*Decimal("0.2") - dd_penalty*Decimal("0.2") - loss_streak_penalty*Decimal("0.1") - safety_penalty*Decimal("0.5")
    return max(Decimal("0"),min(raw,Decimal("1")))

def compare(challenger: ValidationMetrics, champion: ValidationMetrics | None) -> Scorecard:
    cs=_score(challenger)
    if champion is None:
        return Scorecard(cs,None,None,())
    ps=_score(champion)
    improvement=cs-ps
    reasons=()
    return Scorecard(cs,ps,improvement,reasons)
