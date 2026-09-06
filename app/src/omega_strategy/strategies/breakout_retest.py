from omega_strategy.domain.models import StrategyDescriptor, StrategyRole
from omega_strategy.strategies.common import wait_proposal

class BreakoutRetestStrategy:
    descriptor = StrategyDescriptor(
        "BREAKOUT_RETEST_V1","Пробой и ретест","*",
        StrategyRole.LAB,"BREAKOUT_RETEST","1",
        live_permission=False,independent_family="BREAKOUT"
    )
    def evaluate(self, world_model, context):
        if world_model.dominant_regime not in {"BREAKOUT_UP","BREAKOUT_DOWN","COMPRESSION","TRANSITION"}:
            return wait_proposal(self.descriptor,world_model,context,["STRAT_NOT_ELIGIBLE_FOR_REGIME"])
        return wait_proposal(self.descriptor,world_model,context,["STRAT_WAIT"])
