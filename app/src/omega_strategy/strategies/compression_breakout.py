from omega_strategy.domain.models import StrategyDescriptor, StrategyRole
from omega_strategy.strategies.common import wait_proposal

class CompressionBreakoutStrategy:
    descriptor = StrategyDescriptor(
        "COMPRESSION_BREAKOUT_V1","Выход из сжатия","*",
        StrategyRole.LAB,"COMPRESSION_BREAKOUT","1",
        live_permission=False,independent_family="COMPRESSION"
    )
    def evaluate(self, world_model, context):
        if world_model.dominant_regime not in {"COMPRESSION","BREAKOUT_UP","BREAKOUT_DOWN"}:
            return wait_proposal(self.descriptor,world_model,context,["STRAT_NOT_ELIGIBLE_FOR_REGIME"])
        return wait_proposal(self.descriptor,world_model,context,["STRAT_WAIT"])
