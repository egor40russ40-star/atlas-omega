from __future__ import annotations
from decimal import Decimal
from typing import Iterable
from uuid import uuid4
from omega_memory.domain.models import (
    PricePoint, CounterfactualScenario, CounterfactualResult,
    ObservationMode
)

def _pnl(side: str, entry: Decimal, exit: Decimal) -> Decimal:
    return exit-entry if side=="BUY" else entry-exit

def _mfe_mae(side: str, entry: Decimal, points: list[PricePoint]) -> tuple[Decimal,Decimal]:
    if not points:
        return Decimal("0"),Decimal("0")
    high=max(p.high for p in points)
    low=min(p.low for p in points)
    if side=="BUY":
        return max(high-entry,Decimal("0")), max(entry-low,Decimal("0"))
    return max(entry-low,Decimal("0")), max(high-entry,Decimal("0"))

def simulate_basic_scenario(
    scenario: CounterfactualScenario,
    points: Iterable[PricePoint],
) -> CounterfactualResult:
    pts=sorted(points,key=lambda x:x.occurred_at)
    if not pts:
        return CounterfactualResult(
            uuid4(),scenario.scenario_id,scenario.parent_observation_id,
            ObservationMode.COUNTERFACTUAL,None,None,"INCOMPLETE",
            None,None,None,None,None,False,
            {"reason":"MEMORY_COUNTERFACTUAL_PATH_INCOMPLETE"}
        )

    if scenario.scenario_type.value == "NO_TRADE":
        return CounterfactualResult(
            uuid4(),scenario.scenario_id,scenario.parent_observation_id,
            ObservationMode.COUNTERFACTUAL,None,None,"NO_TRADE",
            Decimal("0"),Decimal("0"),Decimal("0"),Decimal("0"),
            int((pts[-1].occurred_at-pts[0].occurred_at).total_seconds()),
            True,{"scenario_version":scenario.scenario_version}
        )

    entry=scenario.entry_price
    entered=False
    entered_at=None
    path_after=[]
    for p in pts:
        if not entered:
            if p.low <= entry <= p.high:
                entered=True
                entered_at=p.occurred_at
                path_after.append(p)
            continue
        path_after.append(p)

    if not entered:
        return CounterfactualResult(
            uuid4(),scenario.scenario_id,scenario.parent_observation_id,
            ObservationMode.COUNTERFACTUAL,None,None,"ENTRY_NOT_REACHED",
            Decimal("0"),None,Decimal("0"),Decimal("0"),
            int((pts[-1].occurred_at-pts[0].occurred_at).total_seconds()),
            True,{"scenario_version":scenario.scenario_version}
        )

    exit_price=path_after[-1].price
    exit_reason="HORIZON_END"
    for p in path_after:
        if scenario.side=="BUY":
            if scenario.stop_price is not None and p.low <= scenario.stop_price:
                exit_price=scenario.stop_price; exit_reason="STOP"; break
            if scenario.take_profit_price is not None and p.high >= scenario.take_profit_price:
                exit_price=scenario.take_profit_price; exit_reason="TAKE_PROFIT"; break
        else:
            if scenario.stop_price is not None and p.high >= scenario.stop_price:
                exit_price=scenario.stop_price; exit_reason="STOP"; break
            if scenario.take_profit_price is not None and p.low <= scenario.take_profit_price:
                exit_price=scenario.take_profit_price; exit_reason="TAKE_PROFIT"; break

    pnl_points=_pnl(scenario.side,entry,exit_price)
    risk_points=None
    if scenario.stop_price is not None:
        risk_points=abs(entry-scenario.stop_price)
    pnl_r=None if not risk_points else pnl_points/risk_points
    mfe,mae=_mfe_mae(scenario.side,entry,path_after)
    duration=int((path_after[-1].occurred_at-entered_at).total_seconds()) if entered_at else None

    return CounterfactualResult(
        uuid4(),scenario.scenario_id,scenario.parent_observation_id,
        ObservationMode.COUNTERFACTUAL,entry,exit_price,exit_reason,
        pnl_points,pnl_r,mfe,mae,duration,True,
        {"scenario_version":scenario.scenario_version}
    )
