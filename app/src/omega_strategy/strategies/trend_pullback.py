from __future__ import annotations
from omega_strategy.domain.models import StrategyDescriptor, StrategyRole
from omega_strategy.strategies.common import wait_proposal

class TrendPullbackStrategy:
    descriptor = StrategyDescriptor(
        "TREND_PULLBACK_V1","Трендовый откат","*",
        StrategyRole.LAB,"TREND_PULLBACK","1",
        live_permission=False,independent_family="TREND"
    )
    def evaluate(self, world_model, context):
        if world_model.dominant_regime not in {"TREND_UP","TREND_DOWN","TRANSITION"}:
            return wait_proposal(self.descriptor,world_model,context,["STRAT_NOT_ELIGIBLE_FOR_REGIME"])
        return wait_proposal(self.descriptor,world_model,context,["STRAT_WAIT"])
