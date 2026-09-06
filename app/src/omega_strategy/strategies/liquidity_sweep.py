from omega_strategy.domain.models import StrategyDescriptor, StrategyRole
from omega_strategy.strategies.common import wait_proposal

class LiquiditySweepStrategy:
    descriptor = StrategyDescriptor(
        "LIQUIDITY_SWEEP_V1","Сбор ликвидности","*",
        StrategyRole.LAB,"LIQUIDITY_SWEEP","1",
        live_permission=False,independent_family="LIQUIDITY"
    )
    def evaluate(self, world_model, context):
        of=world_model.orderflow
        if of is None or not (of.sweep_up or of.sweep_down):
            return wait_proposal(self.descriptor,world_model,context,["STRAT_WAIT"])
        return wait_proposal(self.descriptor,world_model,context,["STRAT_WAIT"])
